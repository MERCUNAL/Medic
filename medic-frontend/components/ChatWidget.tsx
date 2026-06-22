"use client";

import { useState } from "react";
import Sidebar from "./Sidebar";
import ChatWindow from "./ChatWindow";
import { useChat } from "@/hooks/useChat";

type Stage = "ask_role" | "ask_location" | "chatting";

const ROLES = [
    "Doctor",
    "Hospital Procurement",
    "Dealer/Distributor",
    "Individual Buyer",
    "Other",
];

export default function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [stage, setStage] = useState<Stage>("ask_role");
    const [userRole, setUserRole] = useState("");
    const [userLocation, setUserLocation] = useState("");
    const [locationInput, setLocationInput] = useState("");

    const {
        chats,
        currentChatId,
        currentChat,
        setCurrentChatId,
        createNewChat,
        ask,
        loading,
    } = useChat(userRole, userLocation);

    const handleRoleSelect = (role: string) => {
        setUserRole(role);
        setStage("ask_location");
    };

    const handleLocationSubmit = () => {
        if (!locationInput.trim()) return;
        setUserLocation(locationInput.trim());
        setStage("chatting");
    };

    return (
        <>
            {isOpen && (
                <div className="fixed bottom-24 right-6 w-[900px] h-[650px] bg-white rounded-2xl shadow-2xl border border-green-200 flex overflow-hidden z-50">

                    {/* Onboarding — role and location collection */}
                    {stage !== "chatting" && (
                        <div className="relative flex flex-col items-center justify-center w-full gap-6 p-10 bg-green-50">
                            <button
                                onClick={() => setIsOpen(false)}
                                className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-xl"
                            >
                                ✕
                            </button>

                            <h2 className="text-2xl font-bold text-green-700">
                                🩺 Welcome to Medic
                            </h2>

                            {stage === "ask_role" && (
                                <>
                                    <p className="text-gray-500 text-sm">
                                        What best describes your role?
                                    </p>
                                    <div className="flex flex-wrap gap-3 justify-center max-w-md">
                                        {ROLES.map((r) => (
                                            <button
                                                key={r}
                                                onClick={() => handleRoleSelect(r)}
                                                className="bg-white border border-green-300 text-green-700 px-5 py-2 rounded-full text-sm hover:bg-green-100 transition"
                                            >
                                                {r}
                                            </button>
                                        ))}
                                    </div>
                                </>
                            )}

                            {stage === "ask_location" && (
                                <>
                                    <p className="text-gray-500 text-sm">
                                        Which city or region are you purchasing from?
                                    </p>
                                    <p className="text-green-600 text-xs font-medium -mt-3">
                                        Role: {userRole}
                                    </p>
                                    <div className="flex gap-2 w-full max-w-sm">
                                        <input
                                            autoFocus
                                            value={locationInput}
                                            onChange={(e) => setLocationInput(e.target.value)}
                                            onKeyDown={(e) => e.key === "Enter" && handleLocationSubmit()}
                                            placeholder="e.g. Mumbai, Delhi..."
                                            className="flex-1 border border-green-300 rounded-xl px-4 py-2 text-sm text-black outline-none focus:ring-2 focus:ring-green-300"
                                        />
                                        <button
                                            onClick={handleLocationSubmit}
                                            className="bg-green-600 text-white px-4 py-2 rounded-xl text-sm hover:bg-green-700 transition"
                                        >
                                            Continue →
                                        </button>
                                    </div>
                                </>
                            )}
                        </div>
                    )}

                    {/* Full chat with all existing components */}
                    {stage === "chatting" && (
                        <>
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
                                userRole={userRole}
                                userLocation={userLocation}
                            />
                        </>
                    )}
                </div>
            )}

            {/* Floating bubble */}
            <button
                onClick={() => setIsOpen((o) => !o)}
                className="fixed bottom-6 right-6 bg-green-600 hover:bg-green-700 text-white px-6 py-4 rounded-full shadow-xl z-50 transition text-lg"
            >
                {isOpen ? "✕" : "🩺 Medic"}
            </button>
        </>
    );
}