import { Nav } from '@/components/Nav';
import { Hero } from '@/components/Hero';
import { StoryChain } from '@/components/StoryChain';
import { SearchDemo } from '@/components/SearchDemo';
import { CompanyCard } from '@/components/CompanyCard';
import { Connections } from '@/components/Connections';
import { Monitoring } from '@/components/Monitoring';
import { Reports } from '@/components/Reports';
import { Sources } from '@/components/Sources';
import { Limitations } from '@/components/Limitations';
import { FinalCTA } from '@/components/FinalCTA';
import { Footer } from '@/components/Footer';

function App() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <StoryChain />
        <SearchDemo />
        <CompanyCard />
        <Connections />
        <Monitoring />
        <Reports />
        <Sources />
        <Limitations />
        <FinalCTA />
      </main>
      <Footer />
    </>
  );
}

export default App;
