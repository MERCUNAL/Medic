"use client";

import { useState } from "react";

import Sidebar from "./Sidebar";
import ChatWindow from "./ChatWindow";

import { useChat } from "@/hooks/useChat";

export default function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);

    const {
        chats,
        currentChatId,
        currentChat,
        setCurrentChatId,
        createNewChat,
        ask,
        loading,
    } = useChat();

    return (
        <>
            {/* Expanded Widget */}
            {isOpen && (
                <div
                    className="
                        fixed
                        bottom-24
                        right-6
                        w-[900px]
                        h-[650px]
                        bg-white
                        rounded-2xl
                        shadow-2xl
                        border
                        border-green-200
                        flex
                        overflow-hidden
                        z-50
                    "
                >
                    <Sidebar
                        chats={chats}
                        currentChatId={currentChatId}
                        setCurrentChatId={setCurrentChatId}
                        createNewChat={createNewChat}
                    />

                    <ChatWindow
                        currentChat={currentChat}
                        ask={ask}
                        loading={loading}
                        onClose={() => setIsOpen(false)}
                    />
                </div>
            )}

            {/* Floating Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="
                    fixed
                    bottom-6
                    right-6
                    bg-green-600
                    hover:bg-green-700
                    text-white
                    px-6
                    py-4
                    rounded-full
                    shadow-xl
                    z-50
                    transition
                "
            >
                {isOpen ? "✕" : "🩺 Medic"}
            </button>
        </>
    );
}