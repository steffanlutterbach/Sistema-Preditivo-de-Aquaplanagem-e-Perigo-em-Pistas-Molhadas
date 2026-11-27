export default function ErroApi({ mensagem }) {
  return (
    <div className="painel erro" role="alert">
      <strong>Não foi possível falar com a API.</strong>
      <p>{mensagem}</p>
      <p>Confira se o backend está rodando em http://localhost:8000 (passo a passo no README).</p>
    </div>
  );
}
