import ChatWidget from "@/components/ChatWidget";

export default function Home() {
  return (
    <>
      <main style={{ padding: 40, fontFamily: "sans-serif" }}>
        <h1>dKart Medical Equipment</h1>
        <p>Browse and purchase medical equipment.</p>
      </main>
      <ChatWidget />
    </>
  );
}