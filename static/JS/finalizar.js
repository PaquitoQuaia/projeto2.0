
        document.addEventListener(
            "DOMContentLoaded",
            function () {

        const pagamento = document.getElementById("pagamento");
        const extraCartoes = document.getElementById("extra-cartoes");
        const opcaoCartao = document.getElementById("opcao_cartao");
        const cartoesSalvos = document.getElementById("cartoes-salvos");
        const extrasCartao = document.getElementById("extras-cartao");
        const nomeCartao = document.getElementById("nome_cartao");
        const numeroCartao = document.getElementById("numero_cartao");
        const validade = document.getElementById("validade");
        const codigo = document.getElementById("codigo");
        const cartaoCadastrado = document.getElementById("cartao_cadastrado");
        const form = document.querySelector(".form-finalizacao");
        const modalPix = document.getElementById("modal-pix");
        const qrCode = document.getElementById("qr-code");
        const fecharModal = document.querySelector(".fechar-modal");
        const confirmarPix = document.getElementById("confirmar-pix");
        const copiarChave = document.getElementById("copiar-chave");

        function atualizarPagamento() {
            if (!pagamento) return;

            const metodoCartao = pagamento.value === "cartao";

            if (extraCartoes) extraCartoes.style.display = metodoCartao ? "block" : "none";
            if (pagamento.value !== "cartao") {
                if (extrasCartao) extrasCartao.style.display = "none";
                if (cartoesSalvos) cartoesSalvos.style.display = "none";
                if (nomeCartao) nomeCartao.required = false;
                if (numeroCartao) numeroCartao.required = false;
                if (validade) validade.required = false;
                if (codigo) codigo.required = false;
                if (cartaoCadastrado) cartaoCadastrado.required = false;
                return;
            }

            const usarCartaoSalvo = opcaoCartao && opcaoCartao.value === "cadastrado";

            if (extrasCartao) extrasCartao.style.display = usarCartaoSalvo ? "none" : "block";
            if (cartoesSalvos) cartoesSalvos.style.display = usarCartaoSalvo ? "block" : "none";

            if (nomeCartao) nomeCartao.required = !usarCartaoSalvo;
            if (numeroCartao) numeroCartao.required = !usarCartaoSalvo;
            if (validade) validade.required = !usarCartaoSalvo;
            if (codigo) codigo.required = !usarCartaoSalvo;
            if (cartaoCadastrado) cartaoCadastrado.required = usarCartaoSalvo;
        }

        function abrirModalPix() {
            qrCode.src = "/static/imagens/My_Gallery.png";
            modalPix.classList.remove("hidden");
            modalPix.setAttribute("aria-hidden", "false");
        }

        function fecharModalPix() {
            modalPix.classList.add("hidden");
            modalPix.setAttribute("aria-hidden", "true");
        }

        pagamento.addEventListener("change", atualizarPagamento);
        opcaoCartao?.addEventListener("change", atualizarPagamento);
        atualizarPagamento();

        form.addEventListener("submit", function (event) {
            if (pagamento.value === "pix") {
                event.preventDefault();
                abrirModalPix();
            }
        });

        fecharModal.addEventListener("click", fecharModalPix);

        modalPix.addEventListener("click", function (event) {
            if (event.target === modalPix) {
                fecharModalPix();
            }
        });

        confirmarPix.addEventListener("click", function () {
            form.submit();
        });

        copiarChave.addEventListener("click", async function () {
            const chave = "truckparts@pix.com";
            try {
                await navigator.clipboard.writeText(chave);
                copiarChave.textContent = "Chave copiada";
                setTimeout(() => {
                    copiarChave.textContent = "Copiar chave";
                }, 1500);
            } catch (error) {
                copiarChave.textContent = "Não foi possível copiar";
                setTimeout(() => {
                    copiarChave.textContent = "Copiar chave";
                }, 1500);
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && !modalPix.classList.contains("hidden")) {
                fecharModalPix();
            }
        });
    }
);

        const numeroCartao =
            document.getElementById("numero_cartao");


        if (numeroCartao) {


            numeroCartao.addEventListener(
                "input",
                function () {


                    let valor =
                        this.value.replace(
                            /\D/g,
                            ""
                        );


                    valor =
                        valor.substring(
                            0,
                            16
                        );


                    let grupos =
                        valor.match(
                            /.{1,4}/g
                        );


                    this.value =
                        grupos
                            ? grupos.join(" ")
                            : "";


                }
            );

        }



        /* FORMATAÇÃO DA VALIDADE */

        const validade =
            document.getElementById("validade");


        if (validade) {


            validade.addEventListener(
                "input",
                function () {


                    let valor =
                        this.value.replace(
                            /\D/g,
                            ""
                        );


                    valor =
                        valor.substring(
                            0,
                            4
                        );


                    if (valor.length > 2) {


                        valor =
                            valor.substring(
                                0,
                                2
                            )
                            +
                            "/"
                            +
                            valor.substring(
                                2
                            );


                    }


                    this.value =
                        valor;


                }
            );

        }



        /* SOMENTE NÚMEROS NO CVV */

        const codigo =
            document.getElementById("codigo");


        if (codigo) {


            codigo.addEventListener(
                "input",
                function () {


                    this.value =
                        this.value
                            .replace(
                                /\D/g,
                                ""
                            )
                            .substring(
                                0,
                                4
                            );


                }
            );

        }

