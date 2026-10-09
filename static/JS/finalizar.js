
        document.addEventListener(
            "DOMContentLoaded",
            function () {

        const pagamento = document.getElementById("pagamento");
        const extrasCartao = document.getElementById("extras-cartao");
        const nomeCartao = document.getElementById("nome_cartao");
        const numeroCartao = document.getElementById("numero_cartao");
        const validade = document.getElementById("validade");
        const codigo = document.getElementById("codigo");
        const form = document.querySelector(".form-finalizacao");
        const modalPix = document.getElementById("modal-pix");
        const qrCode = document.getElementById("qr-code");
        const fecharModal = document.querySelector(".fechar-modal");
        const confirmarPix = document.getElementById("confirmar-pix");
        const copiarChave = document.getElementById("copiar-chave");

        function atualizarPagamento() {
            if (pagamento.value === "cartao") {
                extrasCartao.style.display = "block";
                nomeCartao.required = true;
                numeroCartao.required = true;
                validade.required = true;
                codigo.required = true;
            } else {
                extrasCartao.style.display = "none";
                nomeCartao.required = false;
                numeroCartao.required = false;
                validade.required = false;
                codigo.required = false;
            }
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

