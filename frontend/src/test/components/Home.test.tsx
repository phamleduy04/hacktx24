import { render, screen } from '@testing-library/react';
import { Home } from '../../components/Home';

test('renders welcome message', () => {
    render(<Home />);
    const messageElement = screen.getByText(/Welcome to the Home Page/i);
    expect(messageElement).toBeInTheDocument();
});