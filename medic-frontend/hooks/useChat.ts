"use client";

import { useEffect, useState } from "react";
import { v4 as uuid } from "uuid";

import {
    Chat,
    Chats,
} from "@/types/chat";

import {
    loadChats,
    saveChats,
} from "@/utils/storage";

import { sendMessage } from "@/services/api";

export function useChat() {
    const [chats, setChats] = useState<Chats>({});
    const [currentChatId, setCurrentChatId] = useState("");
    const [loading, setLoading] = useState(false);

    /*
     * Initial load from localStorage
     */
    useEffect(() => {
        const storedChats = loadChats();

        if (Object.keys(storedChats).length === 0) {
            const id = uuid();

            const initialChats: Chats = {
                [id]: {
                    title: "New Chat",
                    messages: [],
                    suggestions: [],
                },
            };

            setChats(initialChats);
            setCurrentChatId(id);
        } else {
            setChats(storedChats);

            setCurrentChatId(
                Object.keys(storedChats)[0]
            );
        }
    }, []);

    /*
     * Persist chats
     */
    useEffect(() => {
        if (Object.keys(chats).length > 0) {
            saveChats(chats);
        }
    }, [chats]);

    /*
     * Create New Chat
     */
    function createNewChat() {
        const id = uuid();

        const newChat: Chat = {
            title: "New Chat",
            messages: [],
            suggestions: [],
        };

        setChats((prev) => ({
            ...prev,
            [id]: newChat,
        }));

        setCurrentChatId(id);
    }

    /*
     * Send message
     */
    async function ask(userInput: string) {
        if (!userInput.trim()) return;

        if (!currentChatId) return;

        setLoading(true);

        try {
            const currentChat =
                chats[currentChatId];

            /*
             * Add user message immediately
             */
            const updatedChats: Chats = {
                ...chats,

                [currentChatId]: {
                    ...currentChat,

                    title:
                        currentChat.title ===
                        "New Chat"
                            ? userInput.slice(
                                  0,
                                  30
                              )
                            : currentChat.title,

                    messages: [
                        ...currentChat.messages,

                        {
                            role: "user",
                            content: userInput,
                        },
                    ],
                },
            };

            setChats(updatedChats);

            /*
             * Call FastAPI
             */
            const response =
                await sendMessage({
                    query: userInput,

                    thread_id:
                        currentChatId,
                });

            /*
             * Add assistant response
             */
            setChats((prev) => ({
                ...prev,

                [currentChatId]: {
                    ...prev[currentChatId],

                    messages: [
                        ...prev[currentChatId]
                            .messages,

                        {
                            role: "assistant",
                            content:
                                response.answer,
                        },
                    ],

                    suggestions:
                        response.options,
                },
            }));
        } catch (error) {
            console.error(error);

            setChats((prev) => ({
                ...prev,

                [currentChatId]: {
                    ...prev[currentChatId],

                    messages: [
                        ...prev[currentChatId]
                            .messages,

                        {
                            role: "assistant",
                            content:
                                "Sorry, something went wrong.",
                        },
                    ],
                },
            }));
        } finally {
            setLoading(false);
        }
    }

    return {
        chats,

        currentChatId,

        currentChat:
            chats[currentChatId],

        setCurrentChatId,

        createNewChat,

        ask,

        loading,
    };
}