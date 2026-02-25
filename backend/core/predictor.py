import csv
import random
import os
import collections
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sys
import pandas as pd

# Optional TensorFlow import
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TF_AVAILABLE = True
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
except ImportError:
    TF_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Game Rules
RULES = {
    'power': {
        'name': '威力彩 (Super Lotto)',
        'file': 'power.csv',
        'z1_range': (1, 38), 'z1_count': 6,
        'z2_range': (1, 8),  'z2_count': 1,
        'has_special': True
    },
    'big': {
        'name': '大樂透 (Lotto 6/49)',
        'file': 'big.csv',
        'z1_range': (1, 49), 'z1_count': 6,
        'z2_range': (0, 0),  'z2_count': 0,  # 特別號由彩券局開出，玩家不選
        'has_special': False
    },
    '539': {
        'name': '今彩539 (Daily Cash)',
        'file': '539.csv',
        'z1_range': (1, 39), 'z1_count': 5,
        'z2_range': (0, 0),  'z2_count': 0,
        'has_special': False
    }
}

class LotteryPredictor:
    def __init__(self, game_key='power'):
        self.game_key = game_key
        self.game = RULES[game_key]
        self.draws = []
        self.history_vectors = [] 
        
        self.max_num = self.game['z1_range'][1]
        self.transition_matrix = np.zeros((self.max_num + 1, self.max_num + 1))
        self.co_matrix = np.zeros((self.max_num + 1, self.max_num + 1))
        
        # Ensemble
        self.votes = collections.Counter()
        self.strategy_results = {}

    def load_data(self):
        filepath = os.path.join(DATA_DIR, self.game['file'])
        if not os.path.exists(filepath):
            return False, f"Data file not found: {filepath}"
        
        raw_draws = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header: return False, "Empty CSV"
                
                for row in reader:
                    if not row: continue
                    try:
                        date_val = row[0]
                        nums_list = []
                        special = 0
                        z1_count = self.game['z1_count']
                        
                        if len(row) >= z1_count + 1 and row[1].isdigit():
                            for i in range(1, z1_count + 1):
                                if i < len(row) and row[i].isdigit():
                                    nums_list.append(int(row[i]))
                            if self.game['has_special'] and len(row) > z1_count + 1:
                                 if row[z1_count + 1].isdigit():
                                    special = int(row[z1_count + 1])
                        elif len(row) >= 2 and ',' in row[1]:
                            nums = row[1].replace("'", "").replace('"', '')
                            nums_list = [int(n.strip()) for n in nums.split(',') if n.strip().isdigit()]
                            special = int(row[2]) if len(row) > 2 and row[2].isdigit() else 0
                        else:
                            continue
                            
                        if len(nums_list) < z1_count: continue
                        nums_list.sort()
                        raw_draws.append({'date': date_val, 'nums': nums_list, 'special': special})
                    except:
                        continue
        except Exception as e:
            return False, str(e)
        
        self.draws = raw_draws
        self.draws.reverse() # Latest first
        self._build_models()
        return True, "Success"

    def _build_models(self):
        max_num = self.max_num
        z1_count = self.game['z1_count']
        
        # 1. Markov & Co-occurrence
        for i in range(len(self.draws) - 1):
            prev_nums = self.draws[i+1]['nums']
            curr_nums = self.draws[i]['nums']
            for p in prev_nums:
                for c in curr_nums:
                    if 1 <= p <= max_num and 1 <= c <= max_num:
                        self.transition_matrix[p][c] += 1
                        
        row_sums = self.transition_matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        self.transition_matrix = self.transition_matrix / row_sums

        for d in self.draws:
            for n1 in d['nums']:
                for n2 in d['nums']:
                    if n1 != n2:
                        self.co_matrix[n1][n2] += 1

        # 2. History Vectors
        self.history_vectors = []
        for d in self.draws:
            nums = d['nums']
            if not nums: continue
            s = sum(nums)
            span = max(nums) - min(nums)
            odd_cnt = sum(1 for n in nums if n % 2 != 0)
            low_cnt = sum(1 for n in nums if n <= max_num/2)
            
            vec = [
                s / (max_num * z1_count),
                span / max_num,
                odd_cnt / z1_count,
                low_cnt / z1_count,
                np.mean(nums) / max_num,
                (sum(n % 10 for n in nums)) / (9 * z1_count)
            ]
            self.history_vectors.append(vec)

    def _register_vote(self, nums, strategy_name, weight=1.0):
        for n in nums: self.votes[n] += weight
        
    def _generate_zone2(self, weights=None):
        if not self.game['has_special']: return 0
        s_start, s_end = self.game['z2_range']
        pop = range(s_start, s_end + 1)
        if weights and len(weights) == len(pop):
             return random.choices(pop, weights=weights, k=1)[0]
        return random.randint(s_start, s_end)

    # --- Strategies ---

    def strategy_hot(self):
        decay = 0.98
        start, end = self.game['z1_range']
        weights = np.zeros(end - start + 1)
        
        for i, d in enumerate(self.draws):
            for n in d['nums']:
                if start <= n <= end:
                    weights[n - start] += decay ** i
        
        weights = np.maximum(weights, 0.0001)
        res = set()
        pop = range(start, end + 1)
        while len(res) < self.game['z1_count']:
            res.add(random.choices(pop, weights=weights, k=1)[0])
            
        final = sorted(list(res))
        self._register_vote(final, "Hot")
        return {"nums": final, "special": self._generate_zone2(), "name": "熱門動量", "desc": "權重隨時間遞減，強調近期熱門號碼"}

    def strategy_balanced(self):
        count = self.game['z1_count']
        start, end = self.game['z1_range']
        target_sum = (start + end) * count / 2
        
        best_set = None
        min_vio = 9999
        
        for _ in range(300):
            cur = set()
            while len(cur) < count: cur.add(random.randint(start, end))
            nums = sorted(list(cur))
            
            s = sum(nums)
            odd = sum(1 for n in nums if n%2!=0)
            low = sum(1 for n in nums if n<=end/2)
            
            vio = 0
            if not (target_sum * 0.75 <= s <= target_sum * 1.25): vio += 1
            if not (count//2 - 1 <= odd <= count//2 + 1): vio += 1.5
            if not (count//2 - 1 <= low <= count//2 + 1): vio += 1.5
            
            if vio < min_vio:
                min_vio = vio
                best_set = nums
                if vio == 0: break
                
        self._register_vote(best_set, "Balanced", weight=1.5)
        return {"nums": best_set, "special": self._generate_zone2(), "name": "平衡理論", "desc": "符合常態分佈的奇偶/大小/總和結構"}

    def strategy_markov(self):
        if not self.draws: return None
        last = self.draws[0]['nums']
        max_n = self.max_num
        
        # Step 1: Transition
        probs = np.zeros(max_n + 1)
        for n in last: probs += self.transition_matrix[n]
        probs[0] = 0
        if probs.sum() > 0: probs /= probs.sum()
        else: probs = np.ones(max_n+1) / max_n
        
        # Pick 2
        picks = set()
        pop = range(1, max_n + 1)
        while len(picks) < 2:
            picks.add(random.choices(pop, weights=probs[1:], k=1)[0])
            
        # Step 2: Co-occurrence
        while len(picks) < self.game['z1_count']:
            co_w = np.zeros(max_n + 1)
            for p in picks: co_w += self.co_matrix[p]
            for p in picks: co_w[p] = 0
            co_w[0] = 0
            
            if co_w.sum() > 0:
                picks.add(random.choices(pop, weights=co_w[1:], k=1)[0])
            else:
                while len(picks) < self.game['z1_count']: picks.add(random.randint(1, max_n))
                
        final = sorted(list(picks))
        self._register_vote(final, "Markov")
        return {"nums": final, "special": self._generate_zone2(), "name": "馬可夫鏈", "desc": "計算數字間的轉移機率矩陣"}

    def strategy_pattern(self):
        window = 5
        if len(self.history_vectors) < window * 2:
            # Fallback: generate random balanced set
            fallback = self._generate_zone1()
            self._register_vote(fallback, "Pattern")
            return {"nums": fallback, "special": self._generate_zone2(), "name": "歷史重演", "desc": "歷史資料不足，使用隨機取樣"}
            
        curr_vec = np.array(self.history_vectors[:window]).flatten().reshape(1, -1)
        best_sim, best_idx = -1, -1
        
        for i in range(window + 1, min(len(self.history_vectors)-window, 600)):
            cand = np.array(self.history_vectors[i : i+window]).flatten().reshape(1, -1)
            sim = cosine_similarity(curr_vec, cand)[0][0]
            if sim > best_sim:
                best_sim = sim
                best_idx = i
                
        if best_idx > 0:
            target = self.draws[best_idx - 1] # Next draw relative to match
            res = target['nums']
            self._register_vote(res, "Pattern", weight=1.2)
            return {"nums": res, "special": target['special'], "name": "歷史重演", "desc": f"尋找歷史上最相似的K線走勢 (相似度 {best_sim:.2f})"}
        
        # Fallback if no match found
        fallback = self._generate_zone1()
        self._register_vote(fallback, "Pattern")
        return {"nums": fallback, "special": self._generate_zone2(), "name": "歷史重演", "desc": "未找到相似走勢，使用隨機取樣"}

    def strategy_lstm(self):
        if not TF_AVAILABLE:
            return {"nums": [], "special": 0, "name": "深度學習", "desc": "未安裝 TensorFlow", "error": True}
            
        try:
            model_path = os.path.join(BASE_DIR, 'models', f'{self.game_key}_lstm.keras')
            if not os.path.exists(model_path):
                return {"nums": [], "special": 0, "name": "深度學習", "desc": "尚未訓練模型，請先執行 train.py", "error": True}
                
            model = keras.models.load_model(model_path)
            
            # Prepare last window_size (20) elements
            draws = self.draws[:20] # Latest 20
            if len(draws) < 20:
                return {"nums": [], "special": 0, "error": True, "desc": "資料不足 20 期"}
                
            data_arr = []
            max_n = self.max_num
            for d in draws:
                vec = np.zeros(max_n, dtype=np.float32)
                nums = d['nums']
                for n in nums:
                    if 1 <= n <= max_n: vec[n-1] = 1.0
                    
                s_ratio = sum(nums) / (max_n * self.game['z1_count'])
                odd_ratio = sum(1 for n in nums if n % 2 != 0) / self.game['z1_count']
                span_ratio = (max(nums) - min(nums)) / max_n if nums else 0
                
                aux = np.array([s_ratio, odd_ratio, span_ratio], dtype=np.float32)
                combined = np.concatenate([vec, aux])
                data_arr.append(combined)
            
            # Chronological order
            data_arr = np.array(data_arr[::-1])
            last_seq = data_arr.reshape(1, 20, -1)
            
            probs = model.predict(last_seq, verbose=0)[0]
            
            top_idx = probs.argsort()[::-1]
            pred = []
            for idx in top_idx:
                pred.append(int(idx + 1))
                if len(pred) >= self.game['z1_count']: break
            
            pred.sort()
            self._register_vote(pred, "LSTM", weight=2.0)
            return {"nums": pred, "special": self._generate_zone2(), "name": "深度學習(優化版)", "desc": "使用預訓練的 Stacked LSTM 與特徵工程提升穩定度"}
            
        except Exception as e:
            print(e)
            return {"nums": [], "special": 0, "name": "深度學習", "desc": "執行錯誤", "error": True}

    def _generate_zone1(self):
        start, end = self.game['z1_range']
        return sorted(random.sample(range(start, end+1), self.game['z1_count']))

    def strategy_gap(self):
        start, end = self.game['z1_range']
        last_seen = {n: 999 for n in range(start, end+1)}
        freq = collections.Counter()
        
        for idx, d in enumerate(self.draws):
            for n in d['nums']:
                if last_seen.get(n) == 999: last_seen[n] = idx
                freq[n] += 1
                
        ratios = []
        nums_map = []
        total = len(self.draws)
        
        for n in range(start, end+1):
            f = freq[n] if freq[n]>0 else 1
            avg = total / f
            gap = last_seen[n] if last_seen[n]!=999 else total
            ratio = gap/avg if avg>0 else 0
            ratios.append(ratio**2) # weight
            nums_map.append(n)
            
        picks = set()
        while len(picks) < self.game['z1_count']:
            c = random.choices(nums_map, weights=ratios, k=1)[0]
            picks.add(c)
            
        final = sorted(list(picks))
        self._register_vote(final, "Gap")
        return {"nums": final, "special": self._generate_zone2(), "name": "間距追蹤", "desc": "計算長期未出現號碼的平均遺漏值"}

    def strategy_tail(self):
        tails = collections.Counter()
        decay = 0.95
        for i, d in enumerate(self.draws[:50]):
            for n in d['nums']:
                tails[n % 10] += decay**i
        
        pop_t = [k for k,v in tails.items()]
        wei_t = [v for k,v in tails.items()]
        
        picks = set()
        start, end = self.game['z1_range']
        
        while len(picks) < self.game['z1_count']:
            if not pop_t: break 
            t = random.choices(pop_t, weights=wei_t, k=1)[0]
            cands = [n for n in range(start, end+1) if n%10 == t]
            if cands: picks.add(random.choice(cands))
            
        final = sorted(list(picks))
        self._register_vote(final, "Tail")
        return {"nums": final, "special": self._generate_zone2(), "name": "尾數分析", "desc": "追蹤近期高頻尾數趨勢"}

    def strategy_ensemble(self):
        common = self.votes.most_common()
        cands = [n for n, c in common]
        final = sorted(cands[:self.game['z1_count']])
        
        details = []
        for n in final:
            details.append(f"{n}({self.votes[n]:.1f}票)")
            
        desc = "統整所有策略的最高票選結果。細節: " + "、".join(details)
        return {"nums": final, "special": self._generate_zone2(), "name": "綜合預測", "desc": desc}

    def run_all(self):
        # Note: load_data() must be called before run_all()
        if not self.draws:
            return {"error": "No data loaded. Call load_data() first."}
            
        results = [
            self.strategy_hot(),
            self.strategy_balanced(),
            self.strategy_markov(),
            self.strategy_pattern(),
            self.strategy_lstm(),
            self.strategy_gap(),
            self.strategy_tail(),
            # self.strategy_entropy(), # Removed
        ]
        
        # Calculate ensemble last
        results.append(self.strategy_ensemble())
        
        return {
            "game": self.game['name'],
            "last_date": self.draws[0]['date'],
            "total_draws": len(self.draws),
            "strategies": results
        }
