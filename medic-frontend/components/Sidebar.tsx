"use client";

import { Chats } from "@/types/chat";

interface SidebarProps {
    chats: Chats;
    currentChatId: string;
    setCurrentChatId: (id: string) => void;
    createNewChat: () => void;
}

export default function Sidebar({
    chats,
    currentChatId,
    setCurrentChatId,
    createNewChat,
}: SidebarProps) {
    return (
        <div
            className="
                w-64
                bg-gradient-to-b
                from-green-900
                to-green-700
                text-white
                flex
                flex-col
                p-4
            "
        >
            {/* Title */}
            <div className="mb-4">
                <h2 className="text-2xl font-bold">
                    💬 Chats
                </h2>
            </div>

            {/* New Chat Button */}
            <button
                onClick={createNewChat}
                className="
                    w-full
                    bg-white
                    text-green-700
                    rounded-xl
                    py-3
                    font-medium
                    hover:bg-green-50
                    transition
                "
            >
                ➕ New Chat
            </button>

            {/* Chat List */}
            <div
                className="
                    mt-6
                    flex-1
                    overflow-y-auto
                    space-y-2
                "
            >
                {Object.entries(chats).map(
                    ([chatId, chat]) => (
                        <button
                            key={chatId}
                            onClick={() =>
                                setCurrentChatId(chatId)
                            }
                            className={`
                                w-full
                                text-left
                                px-3
                                py-3
                                rounded-xl
                                transition

                                ${
                                    currentChatId ===
                                    chatId
                                        ? "bg-green-500"
                                        : "bg-green-600 hover:bg-green-500"
                                }
                            `}
                        >
                            <div className="font-medium truncate">
                                {chat.title}
                            </div>

                            <div className="text-sm text-green-100 truncate">
                                {chat.messages.length >
                                0
                                    ? chat.messages[
                                          chat
                                              .messages
                                              .length -
                                              1
                                      ].content
                                    : "No messages yet"}
                            </div>
                        </button>
                    )
                )}
            </div>
        </div>
    );
}