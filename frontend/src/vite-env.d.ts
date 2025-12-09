/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_CHAT_SESSION_ENDPOINT: string;
  readonly VITE_CHAT_MESSAGE_ENDPOINT: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
