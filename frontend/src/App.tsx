import CartPanel from "./components/CartPanel";
import ChatPanel from "./components/ChatPanel";
import ReviewPanel from "./components/ReviewPanel";
import "./styles.css";

export default function App() {
  return (
    <div className="app">
      <header>
        <h1>Cart Copilot</h1>
        <p>
          Real listings, real reviews. Nothing here is invented: the review text comes from 141,240
          customer reviews, and prices come from live store listings.
        </p>
      </header>

      <main>
        <div className="column">
          <ChatPanel />
          <ReviewPanel />
        </div>
        <div className="column">
          <CartPanel />
        </div>
      </main>
    </div>
  );
}
