import { useCallback, useEffect, useState } from 'react';
import type { Conversation, Message } from '../types';
import { sendChatMessage } from '../lib/api';

const STORAGE_KEY = 'sre-chat-conversations';
let idCounter = 0;
const nextId = () => `${Date.now()}-${idCounter++}`;

function titleFromMessage(text: string): string {
  const trimmed = text.trim().replace(/\s+/g, ' ');
  return trimmed.length > 42 ? `${trimmed.slice(0, 42)}…` : trimmed || 'New chat';
}

function loadConversations(): Conversation[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Conversation[]) : [];
  } catch {
    return [];
  }
}

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>(loadConversations);
  const [activeId, setActiveId] = useState<string | null>(conversations[0]?.id ?? null);
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
  }, [conversations]);

  const activeConversation = conversations.find((c) => c.id === activeId) ?? null;

  const newChat = useCallback(() => {
    setIsStreaming(false);
    setActiveId(null);
  }, []);

  const deleteConversation = useCallback(
    (id: string) => {
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (id === activeId) setActiveId(null);
    },
    [activeId]
  );

  const send = useCallback(
    async (text: string) => {
      if (!text.trim() || isStreaming) return;

      const userMessage: Message = { id: nextId(), role: 'user', content: text, createdAt: Date.now() };
      const assistantId = nextId();
      const assistantMessage: Message = { id: assistantId, role: 'assistant', content: '', createdAt: Date.now() };

      const targetId = activeConversation ? activeConversation.id : nextId();
      const sessionId = activeConversation?.sessionId ?? null;

      if (activeConversation) {
        setConversations((prev) =>
          prev.map((c) =>
            c.id === targetId ? { ...c, messages: [...c.messages, userMessage, assistantMessage] } : c
          )
        );
      } else {
        const fresh: Conversation = {
          id: targetId,
          title: titleFromMessage(text),
          messages: [userMessage, assistantMessage],
          createdAt: Date.now(),
          sessionId: null,
        };
        setConversations((prev) => [fresh, ...prev]);
        setActiveId(targetId);
      }

      setIsStreaming(true);

      try {
        const response = await sendChatMessage(text, sessionId);
        setConversations((prev) =>
          prev.map((c) =>
            c.id === targetId
              ? {
                  ...c,
                  sessionId: response.session_id,
                  messages: c.messages.map((m) =>
                    m.id === assistantId ? { ...m, content: response.reply } : m
                  ),
                }
              : c
          )
        );
      } catch {
        setConversations((prev) =>
          prev.map((c) =>
            c.id === targetId
              ? {
                  ...c,
                  messages: c.messages.map((m) =>
                    m.id === assistantId
                      ? { ...m, content: 'Sorry, something went wrong reaching the assistant. Please try again.' }
                      : m
                  ),
                }
              : c
          )
        );
      } finally {
        setIsStreaming(false);
      }
    },
    [activeConversation, isStreaming]
  );

  return {
    conversations,
    activeConversation,
    activeId,
    isStreaming,
    setActiveId,
    newChat,
    deleteConversation,
    send,
  };
}
