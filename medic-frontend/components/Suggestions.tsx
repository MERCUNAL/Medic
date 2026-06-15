interface SuggestionsProps {
    suggestions: string[];
    ask: (
        input: string
    ) => Promise<void>;
}

export default function Suggestions({
    suggestions,
    ask,
}: SuggestionsProps) {
    if (suggestions.length === 0) {
        return null;
    }

    return (
        <div
            className="
                border-t
                border-green-200
                bg-white
                p-4
            "
        >
            <div
                className="
                    text-sm
                    font-semibold
                    text-green-700
                    mb-2
                "
            >
                Suggested Questions
            </div>

            <div className="flex flex-wrap gap-2">
                {suggestions.map(
                    (
                        suggestion,
                        index
                    ) => (
                        <button
                            key={index}
                            onClick={() =>
                                ask(
                                    suggestion
                                )
                            }
                            className="
                                border
                                border-green-600
                                text-green-700
                                rounded-xl
                                px-3
                                py-2
                                hover:bg-green-50
                                transition
                            "
                        >
                            {suggestion}
                        </button>
                    )
                )}
            </div>
        </div>
    );
}