import { Chats }
    from "@/types/chat";

const STORAGE_KEY =
    "medic_chats";

export function saveChats(
    chats: Chats
) {

    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(chats)
    );
}

export function loadChats():
    Chats {

    const data =
        localStorage.getItem(
            STORAGE_KEY
        );

    if (!data) {
        return {};
    }

    return JSON.parse(data);
}