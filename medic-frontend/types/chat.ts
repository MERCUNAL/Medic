export interface Message {
    role: "user" | "assistant";
    content: string;
}

export interface Chat {
    title: string;
    messages: Message[];
    suggestions: string[];
}

export interface Chats {
    [chatId: string]: Chat;
}

export interface ChatRequest {
    query: string;
    thread_id: string;
    user_role?: string;
    user_location?: string;
}

export interface ChatResponse {
    answer: string;
    options: string[];
}