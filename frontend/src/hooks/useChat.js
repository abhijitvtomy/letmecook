import { useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import API_BASE from '../config';

export default function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(uuidv4());

  const clearChat = () => {
    setMessages([]);
    setConversationId(uuidv4());
  };

  const sendMessage = useCallback(async (content) => {
    const userMsgId = uuidv4();
    const newMessages = [...messages, { id: userMsgId, role: 'user', content, timestamp: Date.now() }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: conversationId,
          message: content
        })
      });

      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      
      setMessages(prev => [
        ...prev,
        {
          id: uuidv4(),
          role: 'assistant',
          content: data.response,
          recipe: data.recipe || null,
          imageUrl: data.image_url || data.recipe?.image_url || null,
          timestamp: Date.now()
        }
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => [
        ...prev,
        {
          id: uuidv4(),
          role: 'assistant',
          content: `Sorry, I had trouble connecting to the kitchen (${error.message}). Please make sure http://localhost:8001 is running and try again!`,
          timestamp: Date.now()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [messages, conversationId]);

  const sendImage = useCallback(async (base64Image) => {
    const userMsgId = uuidv4();
    const newMessages = [
      ...messages, 
      { id: userMsgId, role: 'user', image: base64Image, content: "What can you make with this?", timestamp: Date.now() }
    ];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/image/identify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: base64Image.includes(',') ? base64Image.split(',')[1] : base64Image })
      });

      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      
      const promptText = `I uploaded an image of ${data.dish_name || 'food'}. Can you provide the recipe?`;
      
      const chatResponse = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: conversationId,
          message: promptText
        })
      });
      
      const chatData = await chatResponse.json();

      setMessages(prev => [
        ...prev,
        {
          id: uuidv4(),
          role: 'assistant',
          content: chatData.response,
          recipe: chatData.recipe || null,
          imageUrl: chatData.image_url || chatData.recipe?.image_url || null,
          timestamp: Date.now()
        }
      ]);
    } catch (error) {
      console.error("Image upload error:", error);
      setMessages(prev => [
        ...prev,
        {
          id: uuidv4(),
          role: 'assistant',
          content: "I couldn't identify that image. Please try again.",
          timestamp: Date.now()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [messages, conversationId]);

  return {
    messages,
    isLoading,
    sendMessage,
    sendImage,
    clearChat,
    conversationId
  };
}
