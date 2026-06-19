import { Message as MessageType } from "@/types/chat";

interface MessageProps {
    message: MessageType;
}

export default function Message({
    message,
}: MessageProps) {
    const isUser =
        message.role === "user";

    return (
        <div
            className={`flex mb-4 ${
                isUser
                    ? "justify-end"
                    : "justify-start"
            }`}
        >
            <div
                className={`
                    max-w-[80%]
                    px-4
                    py-3
                    rounded-2xl
                    whitespace-pre-wrap
                    break-words
                    ${
                        isUser
                            ? "bg-green-200 text-black border border-green-300"
                            : "bg-white text-black border border-green-100 shadow-sm"
                    }
                `}
            >
                {message.content}
            </div>
        </div>
    );
}