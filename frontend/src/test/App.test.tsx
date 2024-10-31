// src/__tests__/App.test.js
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';

test('renders the Home component for the "/" route', () => {
    // Render the App component wrapped in MemoryRouter
    render(
        <MemoryRouter initialEntries={['/']}>
            <App />
        </MemoryRouter>
    );

    // Check if the Home component is in the document by looking for unique content in Home
    expect(screen.getByText(/Welcome to the Home Page/i)).toBeInTheDocument();
});
