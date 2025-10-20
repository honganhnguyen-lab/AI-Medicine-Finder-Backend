"use client";

import { useState } from "react";
import { ChatInterface } from "./chat-interface";

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  image?: string;
  results?: ProductResult[];
};

export type ProductResult = {
  id: string;
  name: string;
  description: string;
  image: string;
  retailers: Retailer[];
};

export type Retailer = {
  name: string;
  price: number;
  url: string;
  availability: "in-stock" | "low-stock" | "out-of-stock";
  rating?: number;
  shippingTime?: string;
};

export function MedicineFinder() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hello! I can help you find medicines and healthcare products. You can describe what you're looking for or upload a photo of the product."
    }
  ]);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSendMessage = async (content: string, image?: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      image
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsProcessing(true);

    try {
      const response = await fetch("/api/identify-product", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          query: content,
          image: image
        })
      });

      if (!response.ok) {
        throw new Error("Failed to identify product");
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          data.confidence === "high"
            ? `I found ${data.products.length} product${
                data.products.length > 1 ? "s" : ""
              } matching your search. ${data.notes || ""}`
            : `Here are some products that might match your search. ${
                data.notes || "Please verify the details before purchasing."
              }`,
        results: data.products.map((product: any, index: number) => ({
          id: `product-${Date.now()}-${index}`,
          name: product.name,
          description: product.description,
          image: `/placeholder.svg?height=200&width=200&query=${encodeURIComponent(
            product.name
          )}`,
          retailers: product.retailers.map((retailer: any) => ({
            name: retailer.name,
            price: retailer.price,
            url: "#",
            availability: retailer.availability,
            rating: retailer.rating,
            shippingTime: retailer.shippingTime
          }))
        }))
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "I'm sorry, I encountered an error while trying to identify the product. Please try again."
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="gradient-bg flex h-screen flex-col">
      <header className="border-b border-border/50 bg-card/50 px-6 py-4 backdrop-blur-sm">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-accent shadow-lg shadow-primary/20">
              <svg
                className="h-7 w-7 text-primary-foreground"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
                />
              </svg>
              <div className="absolute -right-1 -top-1 h-3 w-3 animate-pulse rounded-full bg-accent"></div>
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">
                MediFinder AI
              </h1>
              <p className="text-sm text-muted-foreground">
                Smart Medicine & Product Search
              </p>
            </div>
          </div>
          <div className="hidden items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-2 md:flex">
            <svg
              className="h-4 w-4 text-primary"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <span className="text-sm font-medium text-primary">AI-Powered</span>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-hidden">
        <div className="mx-auto h-full max-w-5xl">
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isProcessing={isProcessing}
          />
        </div>
      </div>
    </div>
  );
}
