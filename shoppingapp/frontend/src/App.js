import React, { useState } from "react";
import axios from "axios";

function App() {
  const [mode, setMode] = useState("signup"); // Toggle between signup and signin
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleAction = async () => {
    const url =
      mode === "signup"
        ? "http://localhost:8001/signup" // Signup microservice
        : "http://localhost:8000/signin"; // Signin microservice

    try {
      const response = await axios.post(url, { username, password });
      setMessage(response.data.message); // Display success message
      setError(""); // Clear error message
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred");
      setMessage(""); // Clear success message
    }
  };

  return (
    <div style={styles.container}>
      <h1>{mode === "signup" ? "Signup" : "Signin"}</h1>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        style={styles.input}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={styles.input}
      />
      <button onClick={handleAction} style={styles.button}>
        {mode === "signup" ? "Signup" : "Signin"}
      </button>
      {message && <p style={styles.successMessage}>{message}</p>}
      {error && <p style={styles.errorMessage}>{error}</p>}
      <button
        onClick={() => setMode(mode === "signup" ? "signin" : "signup")}
        style={styles.toggleButton}
      >
        Switch to {mode === "signup" ? "Signin" : "Signup"}
      </button>
    </div>
  );
}

const styles = {
  container: { maxWidth: "400px", margin: "0 auto", textAlign: "center" },
  input: { display: "block", width: "100%", margin: "10px 0", padding: "10px" },
  button: { padding: "10px 20px", backgroundColor: "#007BFF", color: "#fff" },
  toggleButton: { 
    padding: "10px 20px", 
    marginTop: "10px", 
    backgroundColor: "#6c757d", 
    color: "#fff" 
  },
  successMessage: { color: "green" },
  errorMessage: { color: "red" },
};

export default App;