import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import React, { useState, useEffect, useRef, useCallback } from "react";
import { Toaster } from "@/components/ui/toaster";
import { useToast } from "@/hooks/use-toast";
import Webcam from "react-webcam";

import { Marked } from '@ts-stack/markdown';

type Chat = {
    sender: string;
    message: string;
    img?: string | null;
    timestamp?: string; // HH:MM AM/PM
};

interface Detection {
    tracker_id: number;
    text: string;
    xyxy: [number, number, number, number]; // [x1, y1, x2, y2] format
}

export const Home: React.FC = () => {
    const [query, setQuery] = useState<string>("");
    // const [info, setInfo] = useState<string>("");
    const [chats, setChats] = useState<Chat[]>([]);
    const [imageSrc, setImageSrc] = useState<string>("");

    const chatRef = React.useRef<HTMLDivElement>(null);

    const [isAtTop, setIsAtTop] = useState<boolean>(true);

    const [isResponding, setIsResponding] = useState<boolean>(false);
    const webcamRef = useRef<Webcam>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [detection, setDetection] = useState<Detection[]>([]);
    const [isImageProcessing, setImageProcessing] = useState<boolean>(false);
    const { toast } = useToast();

    const pushChat = (sender: string, message: string, img?: string | null) => {
        setChats((prev) => [...prev, { sender, message, img, timestamp: new Date().toLocaleTimeString() }]);
        setTimeout(() => {
            chatRef.current?.scrollTo({
                top: chatRef.current.scrollHeight,
                behavior: "smooth",
            })
        }, 100);
    };

    useEffect(() => {
        if (chatRef.current) {
            const check = () => {
                if (chatRef.current) {
                    setIsAtTop(chatRef.current.scrollTop === 0);
                }
            }

            chatRef.current.addEventListener("scroll", check);

            return () => {
                chatRef.current?.removeEventListener("scroll", check);
            }
        }
    }, [chatRef]);

    const handleDetect = () => {

        if (isResponding) return;

        // if query is not whitespace
        if (query.trim() === "") return;


        // setInfo(`${query}`); // something happens here
        pushChat("user", query);
        setQuery("");
        setIsResponding(true);

        fetch("https://vectorapi.hacktx24.tech/question", {
        // fetch("http://localhost:8765/question", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "accept": "application/json",
            },
            body: JSON.stringify({ "question": query }),
        })
            .then((res) => res.json())
            .then((data) => {
                pushChat("bot", data.response, data.img);
                setIsResponding(false);
            })
            .catch((err) => {
                console.error(err);
                pushChat("bot", "An error occurred while processing the request");
                setIsResponding(false);
            })

    };
    // Capture the webcam feed, convert it to FormData, and send it to the detection API
    const capture = useCallback(async () => {
        if (!webcamRef.current) return;
        const imageSrc = webcamRef.current.getScreenshot({ width: 640, height: 480 });
        if (imageSrc) setImageSrc(imageSrc); // Display the latest image in your component
        setImageProcessing(true);

        // Convert base64 image to Blob
        const blob = await (await fetch(imageSrc!)).blob();

        // Create FormData and append the blob as a file
        const formData = new FormData();
        formData.append("file", blob, "image.jpg"); // The name "file" should match the expected key in your API

        // Send the FormData to your API
        const response = await fetch("https://microservices.hacktx24.tech/process_image/", {
            method: "POST",
            body: formData,
        });

        const data: Detection[] = await response.json();
        toast({
            title: `#${data[0].tracker_id} detected`,
            description: data[0].text
        })
        console.log(data);
        setDetection(data); // Assume API returns an array of coordinates
        setImageProcessing(false);
    }, [webcamRef, toast]);

    // Draw detection boxes based on returned data
    const drawRectangles = useCallback(() => {
        if (detection.length && canvasRef.current && webcamRef.current) {
            const canvas = canvasRef.current;
            const context = canvas.getContext("2d");

            if (context) {
                // Clear previous drawings
                context.clearRect(0, 0, canvas.width, canvas.height);

                const video = webcamRef.current.video!;
                const videoWidth = video.videoWidth;
                const videoHeight = video.videoHeight;

                // Set canvas dimensions to match the video dimensions
                canvas.width = videoWidth;
                canvas.height = videoHeight;

                // Scale and position each detection based on video dimensions
                detection.forEach(({ tracker_id, text, xyxy }) => {
                    const [x1, y1, x2, y2] = xyxy;

                    // Calculate scaled coordinates
                    const boxX = x1 * videoWidth;
                    const boxY = y1 * videoHeight;
                    const boxWidth = (x2 - x1) * videoWidth;
                    const boxHeight = (y2 - y1) * videoHeight;

                    // Draw bounding box
                    context.beginPath();
                    context.rect(boxX, boxY, boxWidth, boxHeight);
                    context.lineWidth = 2;
                    context.strokeStyle = "red";
                    context.stroke();

                    // Draw text label
                    context.fillStyle = "yellow";
                    context.font = "16px Arial";
                    context.fillText(`${text} (ID: ${tracker_id})`, boxX, boxY - 10);
                });
            }
        }
    }, [detection]);

    useEffect(() => {
        const interval = setInterval(() => {
            capture();
        }, 500); // Adjust capture frequency as needed

        return () => clearInterval(interval);
    }, [capture]);

    useEffect(() => {
        drawRectangles();
    }, [detection, drawRectangles]);


    return (
        <div className="flex flex-col justify-start items-center h-screen max-h-screen overflow-hidden bg-gradient-to-br from-blue-500 to-purple-600">
            <h1 className="text-center text-5xl font-extrabold mb-6 text-yellow-300 mt-10">ANGEL'S PROTECTION</h1>

            {/* <div className="w-full max-w-xl h-80 mb-2">
                {imageSrc ? <img
                    src={imageSrc}
                    alt="Live Stream"
                    className="w-full h-full object-cover rounded-lg"
                /> : <div className="w-full h-full bg-gray-800 flex justify-center items-center rounded-lg animate-pulse">
                    <p className="text-yellow-300">Connecting...</p>
                </div>}
            </div> */}

            <div className="w-full max-w-xl h-80 mb-2 relative">
                <Webcam
                    audio={false}
                    ref={webcamRef}
                    screenshotFormat="image/jpeg"
                    className="w-full h-full object-cover rounded-lg"
                    videoConstraints={{
                        width: 640,
                        height: 480,
                    }}
                />
                <canvas
                    ref={canvasRef}
                    className="w-full h-full object-cover rounded-lg"
                    style={{
                        position: "absolute",
                        top: 0,
                        left: 0,
                        zIndex: 10, // Ensures the canvas is on top
                        overflow: 'visible'
                    }}
                />
            </div>

            {/* {info != "" && <div className="p-4 bg-gray-800 border border-yellow-500 rounded-lg mt-4">
                <p className="text-yellow-300">{info}</p>
            </div>} */}
            {chats.length > 0 && <div className="relative w-full h-full overflow-hidden max-w-xl mt-4 mb-4 animate-max-h">

                <div className={cn("flex pointer-events-none justify-center transition-all duration-300 absolute top-0 left-0 h-16 w-full bg-gradient-to-b from-black/15 to-transparent", isAtTop ? "opacity-0" : "opacity-100")} />


                <div ref={chatRef} className="gap-1 flex flex-col  w-full h-full overflow-y-auto overflow-x-hidden scroll pl-2" >
                    {chats.map((chat, index) => (
                        <>
                            <div key={index} className="flex flex-row justify-between w-full">
                                {chat.sender === "user" && <div className="min-w-10" />}
                                <div className={`p-4 bg-gray-800 border max-w-full w-max text-wrap border-yellow-500 rounded-lg animate-in-up`}>
                                    <p className="text-yellow-300" dangerouslySetInnerHTML={{ __html: Marked.parse(chat.message) }}/>
                                    <p className={cn("text-yellow-300 w-full text-sm opacity-65 mt-1", chat.sender === "bot" ? "text-left" : "text-right")}>{chat.sender === "bot" ? "Bot" : "You"} {chat.timestamp}</p>
                                </div>
                                {chat.sender !== "user" && <div className="min-w-10" />}
                            </div>
                            {chat.img && chat.img !== "" && <div className="w-full flex flex-row justify-center"><img src={chat.img} alt="img" className="w-64 h-64 my-2 border border-yellow-500 rounded-lg" /></div>}
                        </>
                    ))}

                    {isResponding && <div className="flex flex-row justify-between">
                        <div className="p-4 bg-gray-800 border border-yellow-500 rounded-lg animate-pulse">
                            <p className="text-yellow-300">...</p>
                        </div>
                        <div className="min-w-10" />
                    </div>}

                </div>
            </div>}

            <div className="flex mb-4 w-full max-w-xl">
                <form onSubmit={(e) => { e.preventDefault(); handleDetect(); }} className="flex mb-4 w-full max-w-xl items-center">
                    <input
                        type="text"
                        placeholder="Enter Query"
                        disabled={isResponding}
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        className="flex-grow px-4 py-2 border-2 border-yellow-300 rounded-l-lg outline-none bg-gray-800 text-white placeholder-yellow-400"
                    />
                    <Button disabled={isResponding} className="px-4 py-2 bg-yellow-500 border-l border-yellow-600 rounded-r-lg hover:bg-yellow-600 transition-colors ml-2 h-full">
                        DETECT
                    </Button>
                </form>
            </div>
            <Toaster />
        </div>
    );
};

export default Home;
