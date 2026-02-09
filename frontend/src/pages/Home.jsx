// import { useState, useEffect } from 'react';
// import { useSearchParams } from 'react-router-dom';
// import { newsAPI } from '../services/api';
// import { useApp } from '../context/AppContext';
// import CategoryFilter from '../components/CategoryFilter';
// import NewsGrid from '../components/NewsGrid';
// import Pagination from '../components/Pagination';

// const Home = () => {
//   const [searchParams] = useSearchParams();
//   const { language, selectedCategory } = useApp();
//   const [articles, setArticles] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [currentPage, setCurrentPage] = useState(1);
//   const [totalPages, setTotalPages] = useState(1);

//   const searchQuery = searchParams.get('search');

//   useEffect(() => {
//     fetchNews();
//   }, [language, selectedCategory, currentPage, searchQuery]);

//   const fetchNews = async () => {
//     setLoading(true);
//     try {
//       const params = {
//         page: currentPage,
//         limit: 12,
//         language,
//       };

//       if (selectedCategory) {
//         params.category = selectedCategory;
//       }

//       if (searchQuery) {
//         params.search = searchQuery;
//       }

//       const data = await newsAPI.getNews(params);
//       setArticles(data.articles);
//       setTotalPages(data.pages);
//     } catch (error) {
//       console.error('Error fetching news:', error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handlePageChange = (page) => {
//     setCurrentPage(page);
//     window.scrollTo({ top: 0, behavior: 'smooth' });
//   };

//   return (
//     <div>
//       <CategoryFilter />

//       <div className="container mx-auto px-4 py-8">
//         {searchQuery && (
//           <div className="mb-6">
//             <h2 className="text-2xl font-bold text-gray-900">
//               Search results for "{searchQuery}"
//             </h2>
//           </div>
//         )}

//         <NewsGrid articles={articles} loading={loading} />

//         {!loading && articles.length > 0 && (
//           <Pagination
//             currentPage={currentPage}
//             totalPages={totalPages}
//             onPageChange={handlePageChange}
//           />
//         )}
//       </div>
//     </div>
//   );
// };

// export default Home;
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { newsAPI } from '../services/api';
import { useApp } from '../context/AppContext';
import CategoryFilter from '../components/CategoryFilter';
import NewsGrid from '../components/NewsGrid';
import Pagination from '../components/Pagination';

const Home = () => {
  const [searchParams] = useSearchParams();
  const { language, selectedCategory } = useApp();
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [error, setError] = useState(null);

  const searchQuery = searchParams.get('search');

  useEffect(() => {
    fetchNews();
  }, [language, selectedCategory, currentPage, searchQuery]);

  const fetchNews = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = {
        page: currentPage,
        limit: 12,
        language,
      };

      if (selectedCategory) {
        params.category = selectedCategory;
      }

      if (searchQuery) {
        params.search = searchQuery;
      }

      const data = await newsAPI.getNews(params);
      
      // ✅ FIXED: Handle undefined data properly
      if (data && data.articles) {
        setArticles(data.articles);
        setTotalPages(data.pages || 1);
      } else {
        // If no data, set empty array
        setArticles([]);
        setTotalPages(1);
      }
      
    } catch (error) {
      console.error('Error fetching news:', error);
      setError('Failed to load news. Please try again.');
      setArticles([]);
      setTotalPages(1);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div>
      <CategoryFilter />

      <div className="container mx-auto px-4 py-8">
        {/* Search header */}
        {searchQuery && (
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Search results for "{searchQuery}"
            </h2>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-800 dark:text-red-200">{error}</p>
            <button
              onClick={fetchNews}
              className="mt-2 text-sm text-red-600 dark:text-red-400 underline hover:no-underline"
            >
              Try again
            </button>
          </div>
        )}

        {/* News grid */}
        <NewsGrid articles={articles} loading={loading} />

        {/* Pagination */}
        {!loading && !error && articles.length > 0 && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
          />
        )}
      </div>
    </div>
  );
};

export default Home;