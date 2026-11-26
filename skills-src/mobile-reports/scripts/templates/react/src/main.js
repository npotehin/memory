import React from "react"
import { createRoot } from "react-dom/client"
import "./style.css"

function App() {
  return React.createElement("main", null,
    React.createElement("h1", null, "Новое приложение"),
    React.createElement("p", null, "Замените стартовый экран приложением из запроса пользователя."),
  )
}

createRoot(document.getElementById("root")).render(React.createElement(App))
