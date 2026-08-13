"use client";
import { useEffect, useState } from "react";
import { v4 as uuid } from "uuid";
import { Chat, Chats } from "@/types/chat";
import { loadChats, saveChats } from "@/utils/storage";
import { sendMessage } from "@/services/api";

export function useChat(userRole: string = "", userLocation: string = "") {
    const [chats, setChats] = useState<Chats>({});
    const [currentChatId, setCurrentChatId] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const storedChats = loadChats();
        if (Object.keys(storedChats).length === 0) {
            const id = uuid();
            setChats({ [id]: { title: "New Chat", messages: [], suggestions: [] } });
            setCurrentChatId(id);
        } else {
            setChats(storedChats);
            setCurrentChatId(Object.keys(storedChats)[0]);
        }
    }, []);

    useEffect(() => {
        if (Object.keys(chats).length > 0) {
            saveChats(chats);
        }
    }, [chats]);

    function createNewChat() {
        const id = uuid();
        const newChat: Chat = { title: "New Chat", messages: [], suggestions: [] };
        setChats((prev) => ({ ...prev, [id]: newChat }));
        setCurrentChatId(id);
    }

    async function ask(userInput: string) {
        if (!userInput.trim() || !currentChatId) return;
        setLoading(true);

        try {
            const currentChat = chats[currentChatId];

            setChats({
                ...chats,
                [currentChatId]: {
                    ...currentChat,
                    title: currentChat.title === "New Chat"
                        ? userInput.slice(0, 30)
                        : currentChat.title,
                    messages: [
                        ...currentChat.messages,
                        { role: "user", content: userInput },
                    ],
                },
            });

            const response = await sendMessage({
                query: userInput,
                thread_id: currentChatId,
                user_role: userRole,
                user_location: userLocation,
            });

            setChats((prev) => ({
                ...prev,
                [currentChatId]: {
                    ...prev[currentChatId],
                    messages: [
                        ...prev[currentChatId].messages,
                        { role: "assistant", content: response.answer },
                    ],
                    suggestions: response.options,
                },
            }));
        } catch (error) {
            console.error(error);
            setChats((prev) => ({
                ...prev,
                [currentChatId]: {
                    ...prev[currentChatId],
                    messages: [
                        ...prev[currentChatId].messages,
                        { role: "assistant", content: "Sorry, something went wrong." },
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
        currentChat: chats[currentChatId],
        setCurrentChatId,
        createNewChat,
        ask,
        loading,
    };
}