import React from 'react';
import { clsx } from 'clsx';

interface GameSelectorProps {
    selectedPath: string;
    onSelect: (path: string) => void;
}

const GAMES = [
    { id: 'power', label: '威力彩', desc: 'Super Lotto' },
    { id: 'big', label: '大樂透', desc: 'Lotto 6/49' },
    { id: '539', label: '今彩539', desc: 'Daily Cash' },
];

export const GameSelector: React.FC<GameSelectorProps> = ({ selectedPath, onSelect }) => {
    return (
        <div className="bg-red-900 p-2 rounded-2xl border-4 border-amber-500 shadow-2xl inline-flex gap-4">
            {GAMES.map((game) => {
                const isActive = selectedPath === game.id;
                return (
                    <button
                        key={game.id}
                        onClick={() => onSelect(game.id)}
                        className={clsx(
                            "relative px-8 py-3 rounded-xl transition-all duration-200 font-bold text-lg min-w-[140px]",
                            isActive
                                ? "bg-amber-400 text-red-900 shadow-lg scale-105 border-2 border-white"
                                : "bg-red-800 text-red-200 hover:bg-red-700 border-2 border-transparent"
                        )}
                    >
                        <div className="flex flex-col items-center">
                            <span>{game.label}</span>
                            <span className="text-xs opacity-80 uppercase">{game.desc}</span>
                        </div>
                    </button>
                );
            })}
        </div>
    );
};
