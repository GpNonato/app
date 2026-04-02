declare global {
  interface Window {
    api: {
      runBot: () => Promise<void>
    }
  }
}