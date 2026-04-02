import './App.css'

function App() {
  const handleRunBot = (routineCode: string) => {
    window.api.runBot(routineCode);
  };

  const routines = [
    "01.02.03",
    "02.03.04",
    "03.04.05"
  ];

  return (
    <div className="app-container">
      <h1>Selecione o RPA</h1>

      <select className="routine-select" id="routineSelect" defaultValue="">
        <option value="" disabled>Escolha a rotina</option>
        {routines.map((r) => (
          <option key={r} value={r}>{r}</option>
        ))}
      </select>

      <button
        className="run-bot-btn"
        onClick={() => {
          const select = document.getElementById("routineSelect") as HTMLSelectElement;
          if (select && select.value) {
            const routineCode = select.value.replace(/\./g, "");
            handleRunBot(routineCode);
          }
        }}
      >
        Rodar Bot
      </button>
    </div>
  );
}

export default App;