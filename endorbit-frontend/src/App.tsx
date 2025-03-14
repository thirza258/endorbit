import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { Product, ApiResponse } from "./interface";

function App() {
  const [messages, setMessages] = useState<{ text: string; user: string; products?: Product[] }[]>([
    { text: "Hello, how can I assist you?", user: "bot" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const sendMessage = async () => {
    const baseURL = "http://localhost:8000/api/v1/chat/";

    if (input.trim() !== "") {
      setMessages((prevMessages) => [...prevMessages, { text: input, user: "me" }]);
      const userInput = input;
      setInput("");
      setIsLoading(true);
      
      try {
        const response = await axios.post<ApiResponse>(baseURL, { input_user: userInput }, {
          headers: {
            "Content-Type": "application/json",
          },
        });
        
        setMessages((prevMessages) => [
          ...prevMessages,
          { 
            text: response.data.data.response, 
            user: "bot",
            products: response.data.data.products 
          },
        ]);
      } catch (error) {
        console.error("Error fetching AI response:", error);
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: "Sorry, something went wrong.", user: "bot" },
        ]);
      } finally {
        setIsLoading(false);
        if (textareaRef.current) {
          textareaRef.current.style.height = "auto";
        }
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(price);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <div className="bg-blue-600 text-white p-4 shadow-md">
        <h1 className="text-2xl font-bold text-center">Endorbit</h1>
      </div>
      
      <div className="flex-grow overflow-y-auto p-4">
        {messages.map((msg, index) => (
          <div key={index} className="mb-4">
            <div
              className={`${msg.user === "me" ? "flex justify-end" : "flex justify-start"}`}
            >
              <div
                className={`max-w-3xl px-4 py-2 rounded-lg shadow ${
                  msg.user === "me"
                    ? "bg-blue-500 text-white rounded-br-none"
                    : "bg-white text-gray-800 rounded-bl-none"
                }`}
              >
                {msg.text}
              </div>
            </div>
            
            {msg.user === "bot" && msg.products && msg.products.length > 0 && (
              <div className="mt-3 ml-2 space-y-4">
                {msg.products.map((product, productIndex) => (
                  <div key={productIndex} className="bg-white rounded-lg shadow-md overflow-hidden border border-gray-200 max-w-2xl">
                    <div className="p-4">
                      <div className="flex justify-between">
                        <h3 className="text-lg font-semibold text-gray-800">{product.product_name}</h3>
                        <span className="font-bold text-blue-600">{formatPrice(product.retail_price)}</span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{product.brand}</p>
                      <p className="text-sm text-gray-600 mt-2">{product.description}</p>
                      
                      <div className="mt-3 flex justify-between items-center">
                        {product.product_rating && (
                          <div className="flex items-center">
                            <span className="bg-green-500 text-white px-2 py-1 rounded text-xs font-bold">
                              {product.product_rating} ★
                            </span>
                          </div>
                        )}
                        <a 
                          href={product.product_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-sm font-medium text-blue-600 hover:underline"
                        >
                          View Product
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
        
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-200 text-gray-500 px-4 py-2 rounded-lg flex items-center">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div className="flex-shrink-0 p-4 bg-white border-t border-gray-200">
        <div className="flex items-end gap-2 max-w-4xl mx-auto">
          <div className="flex-grow relative">
            <textarea
              ref={textareaRef}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 pr-10 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none min-h-[44px] max-h-[200px] overflow-y-auto"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message here... (Shift+Enter for new line)"
              rows={1}
            />
            <div className="absolute bottom-2 right-2 text-xs text-gray-500">
              Shift+Enter for new line
            </div>
          </div>
          <button
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex-shrink-0 transition-colors h-[44px]"
            onClick={sendMessage}
            disabled={isLoading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;