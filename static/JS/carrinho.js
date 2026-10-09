document.addEventListener('DOMContentLoaded', function () {

    const popup = document.createElement('div');

    popup.id = 'cart-popup';

    Object.assign(popup.style, {
        position: 'fixed',
        right: '20px',
        bottom: '20px',
        background: '#ff2424',
        color: '#fff',
        padding: '12px 18px',
        borderRadius: '10px',
        boxShadow: '0 10px 25px rgba(0,0,0,0.18)',
        fontWeight: 'bold',
        zIndex: '9999',
        opacity: '0',
        transform: 'translateY(10px)',
        transition: 'all 0.25s ease',
        pointerEvents: 'none',

        /* deixa o texto e botão lado a lado */
        display: 'flex',
        alignItems: 'center',
        gap: '15px'
    });

    // Texto da mensagem
    const message = document.createElement('span');

    message.textContent = 'Produto adicionado ao carrinho!';


    // Botão "Ver carrinho"
    const cartButton = document.createElement('a');

    cartButton.href = '/carrinho';

    cartButton.textContent = 'Ver carrinho';

    Object.assign(cartButton.style, {
        background: '#fff',
        color: '#ff2424',
        padding: '7px 12px',
        borderRadius: '7px',
        textDecoration: 'none',
        fontWeight: 'bold',
        cursor: 'pointer',
        whiteSpace: 'nowrap'
    });


    // Adiciona os dois dentro do popup
    popup.appendChild(message);
    popup.appendChild(cartButton);

    document.body.appendChild(popup);


    function showPopup(text) {

        message.textContent = text;

        popup.style.opacity = '1';

        popup.style.transform = 'translateY(0)';

        popup.style.pointerEvents = 'auto';

        clearTimeout(showPopup.timeoutId);

        showPopup.timeoutId = setTimeout(() => {

            popup.style.opacity = '0';

            popup.style.transform = 'translateY(10px)';

            popup.style.pointerEvents = 'none';

        }, 2200);
    }


    document
        .querySelectorAll('form[action*="/add_to_cart/"]')
        .forEach((form) => {

            form.addEventListener('submit', async function (event) {

                event.preventDefault();

                const button = form.querySelector(
                    'button[type="submit"]'
                );


                if (button) {

                    button.disabled = true;

                    const originalText = button.textContent;

                    button.textContent = 'Adicionando...';


                    try {

                        const response = await fetch(
                            form.action,
                            {
                                method: 'POST',

                                headers: {
                                    'X-Requested-With':
                                        'XMLHttpRequest'
                                }
                            }
                        );


                        const data = await response
                            .json()
                            .catch(() => ({
                                success: true,
                                message:
                                    'Produto adicionado ao carrinho!'
                            }));


                        if (
                            response.ok &&
                            data.success !== false
                        ) {

                            showPopup(
                                data.message ||
                                'Produto adicionado ao carrinho!'
                            );

                        } else {

                            showPopup(
                                data.message ||
                                'Não foi possível adicionar ao carrinho.'
                            );
                        }


                    } catch (error) {

                        showPopup(
                            'Erro ao adicionar ao carrinho.'
                        );


                    } finally {

                        button.disabled = false;

                        button.textContent = originalText;
                    }
                }
            });
        });
});