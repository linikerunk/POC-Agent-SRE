import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from 'react';
import { ArrowUp, Check, Copy, Siren } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Conversation } from '../types';

const quickSuggestions = [
  'How do I classify incident severity?',
  'Help me write a postmortem',
  'How do I escalate to on-call?',
  'Explain SLOs and error budgets',
];

interface ChatProps {
  conversation: Conversation | null;
  isStreaming: boolean;
  sidebarOpen: boolean;
  onSend: (text: string) => void;
}

export function Chat({ conversation, isStreaming, sidebarOpen, onSend }: ChatProps) {
  const [inputValue, setInputValue] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const messages = conversation?.messages ?? [];
  const isEmpty = messages.length === 0;

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }, [inputValue]);

  const submit = (text: string) => {
    if (!text.trim() || isStreaming) return;
    onSend(text);
    setInputValue('');
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    submit(inputValue);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submit(inputValue);
    }
  };

  const copyToClipboard = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId((current) => (current === id ? null : current)), 1500);
  };

  const InputBar = (
    <form
      onSubmit={handleSubmit}
      className="flex items-end gap-2 bg-[#2f2f2f] border border-white/10 rounded-[28px] px-4 py-2.5 shadow-[0_4px_24px_rgba(0,0,0,0.3)] focus-within:border-white/25 transition-colors"
    >
      <textarea
        ref={textareaRef}
        rows={1}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Message SRE Assistant…"
        className="flex-1 resize-none bg-transparent text-white placeholder-gray-500 text-[15px] leading-relaxed py-1.5 focus:outline-none max-h-[200px]"
      />
      <button
        type="submit"
        disabled={isStreaming || !inputValue.trim()}
        className="shrink-0 bg-white disabled:bg-white/20 text-black disabled:text-white/40 w-8 h-8 rounded-full flex items-center justify-center transition-colors disabled:cursor-not-allowed"
      >
        <ArrowUp size={18} strokeWidth={2.5} />
      </button>
    </form>
  );

  return (
    <div className="flex flex-col h-[100dvh] flex-1 min-w-0 bg-[#212121]">
      {isEmpty ? (
        <div className="flex-1 flex flex-col items-center justify-center px-4">
          <div className={`w-full max-w-2xl transition-all ${sidebarOpen ? '' : 'md:pl-0'}`}>
            <div className="flex items-center justify-center gap-3 mb-8">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-red-500 to-orange-600 flex items-center justify-center shrink-0">
                <Siren size={20} className="text-white" />
              </div>
              <h1 className="text-[28px] sm:text-[32px] font-semibold text-gray-100">How can I help today?</h1>
            </div>

            {InputBar}

            <div className="flex flex-wrap justify-center gap-2 mt-4">
              {quickSuggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => submit(suggestion)}
                  className="px-3.5 py-2 rounded-full border border-white/10 bg-white/[0.03] text-gray-300 hover:bg-white/[0.08] hover:text-white text-sm transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <>
          <div className="flex-1 overflow-y-auto min-h-0">
            <div className="max-w-3xl mx-auto w-full px-4 sm:px-6">
              <div className="pt-14 md:pt-8 pb-6 space-y-6">
                {messages.map((message) =>
                  message.role === 'user' ? (
                    <div key={message.id} className="flex justify-end animate-fade-in">
                      <div className="max-w-[85%] sm:max-w-[75%] bg-[#2f2f2f] text-gray-100 px-4 py-2.5 rounded-3xl">
                        <p className="text-[15px] leading-relaxed whitespace-pre-wrap break-words">
                          {message.content}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div key={message.id} className="flex gap-3 sm:gap-4 animate-fade-in">
                      <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-red-500 to-orange-600 flex items-center justify-center mt-0.5">
                        <Siren size={15} className="text-white" />
                      </div>
                      <div className="group flex-1 min-w-0 pt-0.5">
                        {message.content === '' && isStreaming ? (
                          <span className="inline-flex gap-1 py-1.5">
                            <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" />
                            <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce [animation-delay:0.12s]" />
                            <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce [animation-delay:0.24s]" />
                          </span>
                        ) : (
                          <div className="prose-chat text-[15px] leading-relaxed text-gray-100">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                          </div>
                        )}

                        {message.content && (
                          <button
                            onClick={() => copyToClipboard(message.id, message.content)}
                            className="mt-1.5 p-1.5 rounded-lg text-gray-500 hover:text-gray-200 hover:bg-white/10 opacity-0 group-hover:opacity-100 transition-all"
                            title="Copy"
                          >
                            {copiedId === message.id ? <Check size={15} /> : <Copy size={15} />}
                          </button>
                        )}
                      </div>
                    </div>
                  )
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>
          </div>

          <div className="shrink-0 px-4 sm:px-6 pb-4 sm:pb-6 pt-2 bg-gradient-to-t from-[#212121] via-[#212121]">
            <div className="max-w-3xl mx-auto">
              {InputBar}
              <p className="text-[11px] text-gray-600 mt-2 text-center">
                SRE Assistant can make mistakes. Verify critical information.
              </p>
            </div>
          </div>
        </>
      )}

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(6px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in { animation: fadeIn 0.25s ease-out; }

        .prose-chat p { margin: 0 0 0.7em; }
        .prose-chat p:last-child { margin-bottom: 0; }
        .prose-chat ul, .prose-chat ol { margin: 0 0 0.7em; padding-left: 1.3em; }
        .prose-chat li { margin: 0.2em 0; }
        .prose-chat pre {
          background: #0d0d0d;
          border: 1px solid rgba(255,255,255,0.1);
          border-radius: 12px;
          padding: 14px 16px;
          overflow-x: auto;
          margin: 0.6em 0;
        }
        .prose-chat code {
          font-family: ui-monospace, Consolas, monospace;
          font-size: 0.85em;
        }
        .prose-chat :not(pre) > code {
          background: rgba(255,255,255,0.08);
          padding: 2px 6px;
          border-radius: 4px;
        }
        .prose-chat h1, .prose-chat h2, .prose-chat h3 {
          font-weight: 600;
          margin: 0.7em 0 0.35em;
        }
        .prose-chat a { color: #fca5a5; text-decoration: underline; }
        .prose-chat table { border-collapse: collapse; margin: 0.6em 0; font-size: 0.9em; }
        .prose-chat th, .prose-chat td { border: 1px solid rgba(255,255,255,0.1); padding: 5px 10px; }

        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.25); }
      `}</style>
    </div>
  );
}