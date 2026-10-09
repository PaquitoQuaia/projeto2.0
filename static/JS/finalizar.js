
      const selectPagamento = document.getElementById('pagamento');
      const extrasCartao = document.getElementById('extras-cartao');

      function atualizarPagamento() {
        const valor = selectPagamento.value;
        const mostrarCartao = valor === 'cartao';
        extrasCartao.classList.toggle('show', mostrarCartao);
      }

      selectPagamento.addEventListener('change', atualizarPagamento);
      atualizarPagamento();
   