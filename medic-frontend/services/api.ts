import {
    ChatRequest,
    ChatResponse,
} from "@/types/chat";

const API_URL =
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000";

export async function sendMessage(
    request: ChatRequest
): Promise<ChatResponse> {

    const response = await fetch(
        `${API_URL}/chat`,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json",
            },

            body: JSON.stringify(
                request
            ),
        }
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch response"
        );
    }

    return response.json();
}