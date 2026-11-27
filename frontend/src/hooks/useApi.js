import { useCallback, useEffect, useState } from "react";

/** Busca dados da API e devolve { dados, erro, carregando, recarregar }. */
export function useApi(buscar, dependencias = []) {
  const [dados, setDados] = useState(null);
  const [erro, setErro] = useState(null);
  const [carregando, setCarregando] = useState(true);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const recarregar = useCallback(() => {
    let ativo = true;
    setCarregando(true);
    buscar()
      .then((resultado) => {
        if (ativo) {
          setDados(resultado);
          setErro(null);
        }
      })
      .catch((e) => ativo && setErro(e.message))
      .finally(() => ativo && setCarregando(false));
    return () => {
      ativo = false;
    };
  }, dependencias);

  useEffect(() => recarregar(), [recarregar]);
  return { dados, erro, carregando, recarregar };
}
