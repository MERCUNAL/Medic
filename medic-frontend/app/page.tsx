import WhatsAppButton from "@/components/WhatsAppButton";

export default function Home() {
  return (
    <>
      <main style={{ padding: 40, fontFamily: "sans-serif" }}>
        <h1>dKart Medical Equipment</h1>
        <p>Browse and purchase medical equipment.</p>
        <p className="text-sm text-gray-500 mt-2">
          Tap WhatsApp at the bottom-right to browse catalog, track orders, or chat with our Medic assistant.
        </p>
      </main>
      <WhatsAppButton />
    </>
  );
}