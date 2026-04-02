import './App.css'

function App() {
  const handleRunBot = () => {
    //window.api.runBot()
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <button
        onClick={handleRunBot}
        style={{
          padding: '20px 40px',
          fontSize: '1.5rem',
          cursor: 'pointer',
          borderRadius: '10px',
          backgroundColor: 'red',
          color: 'white',
          border: 'none'
        }}
      >
        Run Bot
      </button>
    </div>
  )
}

export default App
