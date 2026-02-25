import React from 'react';
import { clsx } from 'clsx';
import { Info } from 'lucide-react';

interface PredictionCardProps {
    name: string;
    desc: string;
    numbers: number[];
    special: number;
    loading?: boolean;
}

export const PredictionCard: React.FC<PredictionCardProps> = ({
    name,
    desc,
    numbers,
    special,
    loading = false,
}) => {
    return (
        <div className="group relative overflow-hidden rounded-[2rem] p-8 bg-amber-50 border-4 border-amber-200 shadow-xl hover:shadow-amber-500/40 hover:border-amber-400 transition-all duration-300 transform hover:-translate-y-1">

            {/* Header */}
            <div className="mb-6 border-b-2 border-amber-200 pb-4">
                <div className="flex justify-between items-center mb-3">
                    <h3 className="text-2xl font-black text-red-900 tracking-wide drop-shadow-sm">
                        {loading ? '載入中...' : name}
                    </h3>
                    {loading && <div className="animate-spin w-6 h-6 border-4 border-red-600 border-t-transparent rounded-full" />}
                </div>

                {/* Principle Annotation */}
                <div className="flex items-start gap-2 text-red-800 text-sm font-bold bg-amber-100/50 p-3 rounded-xl border border-amber-200">
                    <Info className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
                    <span className="leading-relaxed">{loading ? '等待伺服器運算...' : desc}</span>
                </div>
            </div>

            {/* Numbers Grid */}
            <div className="flex flex-wrap gap-4 justify-center py-2">
                {loading ? (
                    Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} className="w-14 h-14 rounded-full bg-gray-200 animate-pulse border-2 border-gray-300" />
                    ))
                ) : (
                    <>
                        {/* Normal Numbers: Red Ball, White Text */}
                        {numbers.map((num, idx) => (
                            <div
                                key={`${num}-${idx}`}
                                className="w-14 h-14 md:w-16 md:h-16 rounded-full bg-gradient-to-br from-red-600 to-red-800 shadow-[0_4px_8px_rgba(0,0,0,0.4)] flex items-center justify-center font-black text-white text-2xl md:text-3xl border-2 border-red-500 transform group-hover:scale-110 transition-transform duration-300"
                            >
                                {num}
                            </div>
                        ))}

                        {/* Special Number: Gold Ball, Red Text */}
                        {special > 0 && (
                            <div className="w-14 h-14 md:w-16 md:h-16 rounded-full bg-gradient-to-br from-yellow-400 to-amber-500 shadow-[0_4px_8px_rgba(0,0,0,0.4)] flex items-center justify-center font-black text-red-900 text-2xl md:text-3xl border-2 border-yellow-300 transform group-hover:scale-110 transition-transform duration-300 ml-2">
                                {special}
                            </div>
                        )}
                    </>
                )}
            </div>

            {/* Decoration */}
            <div className="absolute top-0 right-0 w-20 h-20 bg-amber-100 rounded-bl-[3rem] -z-0 opacity-50" />
        </div>
    );
};
