import { useState } from "react";
import Header from "./components/Header/Header";
import Alertas from "./pages/Alertas";
import Dashboard from "./pages/Dashboard";
import Mapa from "./pages/Mapa";

const PAGINAS = { dashboard: Dashboard, mapa: Mapa, alertas: Alertas };

export default function App() {
  const [pagina, setPagina] = useState("dashboard");
  const Pagina = PAGINAS[pagina];
  return (
    <>
      <Header pagina={pagina} onNavegar={setPagina} />
      <main className="conteudo">
        <Pagina />
      </main>
      <footer className="rodape">
        Classificação experimental com dados simulados. Não use para orientar motoristas.
      </footer>
    </>
  );
}
