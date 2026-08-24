"use client";
import { useState } from "react";

const WA_SERVICE_URL = process.env.NEXT_PUBLIC_WHATSAPP_SERVICE_URL || "http://localhost:8001";
const WA_NUMBER = process.env.NEXT_PUBLIC_WHATSAPP_NUMBER || "919999999999";

export default function WhatsAppButton() {
  const [loading, setLoading] = useState(false);

  async function handleClick() {
    setLoading(true);
    try {
      // Try to create a linked REF if user has a stored JWT/phone in localStorage (site auth)
      // Website has authentication via login – we look for common keys
      let token: string | null = null;
      let phone: string | null = null;
      let role: string | null = null;
      let location: string | null = null;
      if (typeof window !== "undefined") {
        token = localStorage.getItem("auth_token") || localStorage.getItem("jwt") || localStorage.getItem("token");
        phone = localStorage.getItem("phone") || localStorage.getItem("user_phone") || localStorage.getItem("whatsapp_phone");
        role = localStorage.getItem("user_role") || localStorage.getItem("role");
        location = localStorage.getItem("user_location") || localStorage.getItem("location");
        // also try to parse user object
        const userStr = localStorage.getItem("user");
        if (userStr) {
          try {
            const u = JSON.parse(userStr);
            phone = phone || u.phone || u.phoneNumber || u.mobile;
            role = role || u.role;
            location = location || u.location || u.city;
            token = token || u.token;
          } catch {}
        }
      }

      let waLink = `https://wa.me/${WA_NUMBER}?text=Hi`;

      // If we have phone or token, ask backend to create a REF link (for mock order linking)
      if (phone || token) {
        try {
          const res = await fetch(`${WA_SERVICE_URL}/auth/link`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ phone: phone || undefined, token: token || undefined, role: role || undefined, location: location || undefined }),
          });
          if (res.ok) {
            const data = await res.json();
            waLink = data.wa_link || waLink;
          }
        } catch (e) {
          console.warn("WhatsApp link creation failed, using direct wa.me", e);
        }
      }

      window.open(waLink, "_blank", "noopener,noreferrer");
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      aria-label="Chat on WhatsApp"
      className="fixed bottom-6 right-6 bg-[#25D366] hover:bg-[#128C7E] text-white px-6 py-4 rounded-full shadow-xl z-50 transition text-lg flex items-center gap-2 disabled:opacity-60"
    >
      <svg viewBox="0 0 32 32" width="22" height="22" fill="white" aria-hidden>
        <path d="M16 3.2c-7.07 0-12.8 5.73-12.8 12.8 0 2.26.59 4.47 1.71 6.41L3.2 28.8l6.55-1.71A12.76 12.76 0 0016 28.8c7.07 0 12.8-5.73 12.8-12.8S23.07 3.2 16 3.2zm0 23.04a10.2 10.2 0 01-5.2-1.43l-.37-.22-3.89 1.02 1.02-3.79-.24-.39A10.2 10.2 0 015.76 16c0-5.63 4.58-10.24 10.24-10.24S26.24 10.37 26.24 16 21.63 26.24 16 26.24zm5.62-7.68c-.31-.16-1.83-.9-2.11-1-.28-.1-.49-.16-.7.16-.21.31-.8 1-.98 1.2-.18.21-.36.24-.67.08-.31-.16-1.31-.48-2.49-1.53-.92-.82-1.54-1.83-1.72-2.14-.18-.31-.02-.48.14-.63.14-.14.31-.36.47-.54.16-.18.21-.31.31-.52.1-.21.05-.39-.03-.54-.08-.16-.7-1.69-.96-2.31-.25-.61-.51-.52-.7-.53h-.6c-.21 0-.54.08-.82.39-.28.31-1.08 1.06-1.08 2.58s1.11 2.99 1.26 3.2c.16.21 2.18 3.33 5.28 4.67.74.32 1.31.51 1.76.65.74.23 1.41.2 1.94.12.59-.09 1.83-.75 2.09-1.47.26-.73.26-1.35.18-1.47-.08-.13-.28-.21-.59-.37z" />
      </svg>
      {loading ? "Opening…" : "WhatsApp"}
    </button>
  );
}
