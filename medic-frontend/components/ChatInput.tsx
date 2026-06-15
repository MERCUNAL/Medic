"use client";

import { useState } from "react";

interface ChatInputProps {
    ask: (
        input: string
    ) => Promise<void>;

    loading: boolean;
}

export default function ChatInput({
    ask,
    loading,
}: ChatInputProps) {
    const [input, setInput] =
        useState("");

    async function handleSend() {
        const text =
            input.trim();

        if (!text) {
            return;
        }

        setInput("");

        await ask(text);
    }

    return (
        <div
            className="
                p-4
                bg-white
                border-t
                border-green-200
                flex
                gap-2
            "
        >
            <input
                value={input}
                onChange={(e) =>
                    setInput(
                        e.target.value
                    )
                }
                onKeyDown={(
                    e
                ) => {
                    if (
                        e.key ===
                            "Enter" &&
                        !loading
                    ) {
                        handleSend();
                    }
                }}
                placeholder="Ask a medical question..."
                className="
                    flex-1
                    border
                    border-green-300
                    rounded-xl
                    px-4
                    py-3
                    outline-none
                    focus:ring-2
                    focus:ring-green-300
                "
            />

            <button
                onClick={
                    handleSend
                }
                disabled={loading}
                className="
                    bg-green-600
                    text-white
                    px-6
                    rounded-xl
                    disabled:opacity-50
                    hover:bg-green-700
                    transition
                "
            >
                {loading
                    ? "..."
                    : "Send"}
            </button>
        </div>
    );
}