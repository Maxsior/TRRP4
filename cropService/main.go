package main

import (
	"./imageCrop"
	"bytes"
	"fmt"
	"github.com/golang/protobuf/proto"
	"image"
	"image/draw"
	"image/jpeg"
	"image/png"
	_ "image/png"
	"io/ioutil"
	"net/http"
	"os"
	"time"
)

func writeResponse(w http.ResponseWriter, image []byte, ok bool, message string ) {
	respProto := imageCrop.Answer{Image: image, Ok: ok, Message: message}
	resp, err := proto.Marshal(&respProto)
	if err != nil{
		fmt.Println("proto object marshall error")
	}

	////для вывода хэша
	//h := md5.New()
	//h.Write(resp)
	//fmt.Printf("transmitted data hash is %x\n", h.Sum(nil))

	wroteLen, err := w.Write(resp)
	fmt.Println(wroteLen)
	fmt.Println(err)
}

func cropImage(w http.ResponseWriter, r *http.Request){
	//читаю тело запроса
	body, err := ioutil.ReadAll(r.Body)
	if err != nil {
		writeResponse(w, []byte{}, false, "request body read error")
		return
	}
	if len(body) == 0 {
		writeResponse(w, []byte{}, false, "request body is empty")
		return
	}
	var req imageCrop.Crop
	err = proto.Unmarshal(body, &req)
	if err != nil {
		writeResponse(w, []byte{}, false, fmt.Sprintf("unmarshall error \n"))
		return
	}

	input, imageFormat, err := image.Decode(bytes.NewReader(req.Image))
	if err != nil {
		writeResponse(w, []byte{}, false, "image decode error")
		return
	}


	resRect := image.Rect(int(req.TopLeft.X), int(req.TopLeft.Y), int(req.BottomRight.X), int(req.BottomRight.Y))
	res := image.NewRGBA(resRect)
	draw.Draw(res, resRect, input, resRect.Min, draw.Src)

	respWriter := bytes.NewBuffer([]byte{})
	if imageFormat == "png" {
		err = png.Encode(respWriter, res)
	} else {
		err = jpeg.Encode(respWriter, res, &jpeg.Options{Quality: 100})
	}
	if err != nil {
		writeResponse(w, []byte{}, false, "image encode error")
		return
	}

	writeResponse(w, respWriter.Bytes(), true, "")
}

type config struct {
	ListenPort       string `json:"listenPort"`
}

func main(){
	address, ok := os.LookupEnv("TRRP4_CROP_ADDR")
	if !ok {
		fmt.Println("env TRRP4_CROP_ADDR not found")
		return
	}



	fmt.Println("Server is listening at " + address)
	mux := http.NewServeMux()
	mux.HandleFunc("/crop", func(w http.ResponseWriter, r *http.Request) {
		cropImage(w, r)
	})

	srv := &http.Server{
		ReadHeaderTimeout: 5 * time.Second,
		WriteTimeout:      30 * time.Second,
		Handler:           mux,
		Addr:              address,
	}
	srv.ListenAndServe()
}
