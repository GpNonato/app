export {};

declare global {
  interface Window {
    api: {
      runBot: () => void;
    };
  }
}