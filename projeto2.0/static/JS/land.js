let produtoAtual = 0;

function getProdutosSlides() {
  return document.querySelectorAll('.prod-slide');
}

function mostrarProduto(numero) {
  const produtosSlides = getProdutosSlides();

  if (!produtosSlides.length) return;

  if (numero < 0) {
    produtoAtual = produtosSlides.length - 1;
  } else if (numero >= produtosSlides.length) {
    produtoAtual = 0;
  } else {
    produtoAtual = numero;
  }

  const radioAtual = document.getElementById('p_slide' + (produtoAtual + 1));
  if (radioAtual) {
    radioAtual.checked = true;
  }
}

function proximoProduto() {
  mostrarProduto(produtoAtual + 1);
}

function produtoAnterior() {
  mostrarProduto(produtoAtual - 1);
}

document.addEventListener('DOMContentLoaded', function () {
  const produtosSlides = getProdutosSlides();
  if (produtosSlides.length) {
    produtoAtual = 0;
  }

  const botaoProximo = document.querySelector('.seta-direita');
  if (botaoProximo) {
    botaoProximo.addEventListener('click', proximoProduto);
  }

  const botaoAnterior = document.querySelector('.seta-esquerda');
  if (botaoAnterior) {
    botaoAnterior.addEventListener('click', produtoAnterior);
  }

  let slideAtual = 1;
  const totalSlides = 3;

  setInterval(() => {
    slideAtual += 1;

    if (slideAtual > totalSlides) {
      slideAtual = 1;
    }

    const slidePrincipal = document.getElementById('slide' + slideAtual);
    if (slidePrincipal) {
      slidePrincipal.checked = true;
    }
  }, 4000);
});
