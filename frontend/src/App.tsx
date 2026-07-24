import { useState } from 'react';
import { Chat } from './components/Chat';
import { useConversations } from './hooks/useConversations';

function App() {
  const { activeConversation, isStreaming, send } = useConversations();
  const [sidebarOpen] = useState(() => typeof window !== 'undefined' && window.innerWidth >= 768);

  return (
    <div className="flex h-[100dvh] w-full overflow-hidden">
      <Chat conversation={activeConversation} isStreaming={isStreaming} sidebarOpen={sidebarOpen} onSend={send} />
    </div>
  );
}

export default App;