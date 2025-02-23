import React from 'react'
import { Link } from 'react-router-dom'
import { ChevronUp, ChevronDown } from 'lucide-react'
import { Word } from '../services/api'

export type WordSortKey = 
  | 'word_hindi_text'
  | 'word_english_text'
  | 'word_meaning'
  | 'word_part_of_speech'
  | 'correct_count'
  | 'wrong_count';

interface WordsTableProps {
  words: Word[]
  sortKey: WordSortKey
  sortDirection: 'asc' | 'desc'
  onSort: (key: WordSortKey) => void
}

export default function WordsTable({ words, sortKey, sortDirection, onSort }: WordsTableProps) {
  return (
    <div className="overflow-x-auto bg-white dark:bg-gray-800 rounded-lg shadow">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-900">
          <tr>
            {(['word_hindi_text', 'word_english_text', 'word_meaning', 'correct_count', 'wrong_count'] as const).map((key) => (
              <th
                key={key}
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800"
                onClick={() => onSort(key)}
              >
                <div className="flex items-center space-x-1">
                  <span>
                    {key === 'correct_count' ? 'Correct' :
                     key === 'wrong_count' ? 'Wrong' :
                     key.charAt(0).toUpperCase() + key.slice(1)}
                  </span>
                  {sortKey === key && (
                    sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
          {words.map((word) => (
            <tr key={word.word_id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td className="px-6 py-4 whitespace-nowrap">
                <Link
                  to={`/words/${word.word_id}`}
                  className="text-blue-600 dark:text-blue-400 hover:underline"
                >
                  {word.word_hindi_text}
                </Link>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                {word.word_english_text}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                {word.word_meaning}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-green-500 dark:text-green-400">
                {word.word_part_of_speech}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-red-500 dark:text-red-400">
                {word.word_meaning}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
