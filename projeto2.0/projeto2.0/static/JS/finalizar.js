

        document.addEventListener(
            "DOMContentLoaded",
            function () {


                const pagamento =
                    document.getElementById("pagamento");


                const extrasCartao =
                    document.getElementById("extras-cartao");


                const nomeCartao =
                    document.getElementById("nome_cartao");


                const numeroCartao =
                    document.getElementById("numero_cartao");


                const validade =
                    document.getElementById("validade");


                const codigo =
                    document.getElementById("codigo");



                function atualizarPagamento() {


                    if (pagamento.value === "cartao") {


                        extrasCartao.style.display =
                            "block";


                        nomeCartao.required =
                            true;


                        numeroCartao.required =
                            true;


                        validade.required =
                            true;


                        codigo.required =
                            true;


                    }


                    else {


                        extrasCartao.style.display =
                            "none";


                        nomeCartao.required =
                            false;


                        numeroCartao.required =
                            false;


                        validade.required =
                            false;


                        codigo.required =
                            false;


                    }

                }



                pagamento.addEventListener(
                    "change",
                    atualizarPagamento
                );



                atualizarPagamento();


            }
        );



        /* FORMATAÇÃO DO CARTÃO */

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
