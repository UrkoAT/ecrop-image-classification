const RABBIT_CONFIG = {
    HOST: "rabbitmq",
    PORT: "5672",
    USER: "node-publisher",
    PASSWORD: "F]k[N$u6SMY2Rum-",
}

const IMAGES_CONFIG = {
    EXCHANGE: "images",
    QUEUE: "images.process",
};

const sendRequest = (channel, body, callbackQueue) => {
    let corrId = crypto.randomUUID();
    channel.publish(
        exchange=IMAGES_CONFIG.EXCHANGE,
        routingKey=IMAGES_CONFIG.QUEUE,
        body,
        {
            replyTo: callbackQueue,
            correlationId: corrId,
        }
    );
};

msg.payload = await (
    async () => {
        let response = null;
        const conn = await amqplib.connect(
            `amqp://${RABBIT_CONFIG.USER}:${RABBIT_CONFIG.PASSWORD}@${RABBIT_CONFIG.HOST}:${RABBIT_CONFIG.PORT}`
        );
        
        const ch = await conn.createChannel();

        const callbackQueue = await ch.assertQueue(
            "",
            {
                exclusive: true,
            }
        );
        

        ch.consume(
            callbackQueue.queue,
            (mg) => {
                response = mg.content.toString();
                ch.ack(mg);
            },
            {
                noAck: false,
            }
        );
        
        sendRequest(ch, msg.payload, callbackQueue.queue);

        while(!response) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        ch.close();
        conn.close();

        return response;
    }
)();

