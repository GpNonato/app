import './App.css'

function App() {
  const handleRunBot = () => {
    window.api.runBot();
  };

  return (
    <div>
      <h1>Meu App</h1>
      <button onClick={handleRunBot}>
        Rodar Bot
      </button>
    </div>
  );
}

export default App;