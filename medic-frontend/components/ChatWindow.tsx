"use client";

import { useRef, useEffect } from "react";
import { Chat } from "@/types/chat";
import Message from "./Message";
import Suggestions from "./Suggestions";
import ChatInput from "./ChatInput";

interface ChatWindowProps {
    currentChat?: Chat;
    ask: (input: string) => Promise<void>;
    loading: boolean;
    onClose: () => void;
    userRole?: string;
    userLocation?: string;
}

export default function ChatWindow({
    currentChat,
    ask,
    loading,
    onClose,
    userRole,
    userLocation,
}: ChatWindowProps) {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [currentChat?.messages]);

    return (
        <div className="flex-1 flex flex-col bg-green-50">

            {/* Header */}
            <div className="flex justify-between items-center p-4 border-b border-green-200 bg-white">
                <div>
                    <h1 className="text-2xl font-bold text-green-700">
                        🩺 Medic
                    </h1>
                    <p className="text-sm text-gray-500">
                        Your AI medical support assistant
                    </p>
                    {/* Context badge */}
                    {userRole && userLocation && (
                        <p className="text-xs text-green-600 font-medium mt-0.5">
                            {userRole} · {userLocation}
                        </p>
                    )}
                </div>
                <button onClick={onClose} className="text-2xl text-gray-500">
                    ×
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6">
                {!currentChat || currentChat.messages.length === 0 ? (
                    <div className="text-center text-gray-500 mt-20">
                        Ask a medical question to get started.
                    </div>
                ) : (
                    currentChat.messages.map((message, index) => (
                        <Message key={index} message={message} />
                    ))
                )}
                {loading && (
                    <div className="text-gray-500">Thinking...</div>
                )}
                <div ref={bottomRef} />
            </div>

            <Suggestions
                suggestions={currentChat?.suggestions ?? []}
                ask={ask}
            />

            <ChatInput ask={ask} loading={loading} />
        </div>
    );
}