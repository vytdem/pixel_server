class Pixel {
    constructor() {
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.ctx.imageSmoothingEnabled = false;

        this.height = 350;
        this.width = 350;

        this.data = new Uint8ClampedArray(this.width * this.height * 4);

        this.ws = new WebsocketHandler();
        this.ws.ws.onmessage = this.onMessage.bind(this);

        document.getElementById('pixel').addEventListener('click', (e) => {
            this.openPixel();
        });

        // this.data[0] = 255;
        // this.data[1] = 166;
        // this.data[2] = 82;
        // this.data[3] = 255;
        //
        // this.data[4] = 242;
        // this.data[5] = 189;
        // this.data[6] = 82;
        // this.data[7] = 255;
        //
        // this.data[8] = 125;
        // this.data[9] = 205;
        // this.data[10] = 182;
        // this.data[11] = 255;
        //
        // this.data[12] = 255;
        // this.data[13] = 255;
        // this.data[14] = 255;
        // this.data[15] = 255;

        this.updateData();
        this.renderByteData();
    }

    updateData()
    {
        let xhr = new XMLHttpRequest();
        xhr.open("GET", "/init/");
        xhr.responseType = "blob";
        xhr.onload = function (event) {
            // console.log('load');
        };

        xhr.addEventListener("readystatechange", () => {
            if (xhr.readyState === 4 && xhr.status === 200) {
                // console.log(xhr.response);
                // let data = xhr.response.arrayBuffer().then((result) => {
                //     console.log(result, new Uint8ClampedArray(result));

                    // const c = document.getElementById('canvas');
                    const cx = this.canvas.getContext('2d');
                    let img = new Image;

                    img.onload = (e) => {
                        cx.drawImage(img, 0, 0);

                        // this.data = cx.getImageData(0, 0, 350, 350).data;
                        // console.log(this.data, this.width, this.height);
                        // this.data = new Uint8ClampedArray(xhr.response);
                        // console.log(xhr.response, this.data);
                        // this.renderByteData();
                    };
                    img.src = URL.createObjectURL(xhr.response);
                // });

            } else if (xhr.readyState === 4) {
                console.log("could not fetch the data");
            }
        });

        xhr.send();
    }

    onMessage(e)
    {
        console.log("Received: ", e);

        try {
            let data = JSON.parse(e.data);
            let pixelData = data.data;

            const cx = this.canvas.getContext('2d');

            cx.fillStyle = "rgba("+ pixelData.r +","+ pixelData.g +","+ pixelData.b +",1)";
            cx.fillRect(pixelData.x, pixelData.y, 1, 1);
        } catch (e) {
            console.log(e);
        }
    }

    renderByteData()
    {
        let imageData = new ImageData(this.data, this.width, this.height);
        this.ctx.putImageData(imageData, 0, 0);
    }

    openPixel()
    {
        this.ws.sendMessage();
    }
}

document.addEventListener("DOMContentLoaded", function(event) {
    const pixel = new Pixel();
});
