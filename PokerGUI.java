package org.example;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.image.BufferedImage;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.TreeMap;
import java.util.function.BiFunction; // Import the BiFunction interface

public class PokerGUI extends JFrame {
    // --- UI Components (marked as final as they are initialized only once) ---
    private final JComboBox<Integer> playerCountSelector;
    private final JTextField flopField, turnField, simulationsField;
    private final JTextArea resultArea;
    private final JButton runButton, resetButton;

    // --- Panels (marked as final) ---
    private final JPanel inputFieldsPanel;
    private final JPanel pickedCardsPanel;
    private final JPanel communityCardsDisplayPanel;
    private final JPanel cardSelectionPanel;

    // --- Data Storage ---
    private final ArrayList<JTextField> playerCardFields = new ArrayList<>();
    private final ArrayList<JPanel> playerDisplayPanels = new ArrayList<>();
    private final ArrayList<JButton> cardButtons = new ArrayList<>();
    private final HashMap<String, ImageIcon> cardImages = new HashMap<>();

    public static void main(String[] args) {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }

        SwingUtilities.invokeLater(() -> {
            PokerGUI gui = new PokerGUI();
            gui.setVisible(true);
        });
    }

    public PokerGUI() {
        // --- Frame Setup ---
        setTitle("Poker Equity Calculator");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout(10, 10));

        // --- Load Card Assets ---
        loadCardImages();

        // --- Panel Initializations ---
        JPanel topPanel = new JPanel(new BorderLayout(10, 10));
        JPanel bottomPanel = new JPanel(new BorderLayout(10, 10));
        JPanel mainContentPanel = new JPanel(new GridLayout(1, 2, 10, 10));

        inputFieldsPanel = new JPanel();
        inputFieldsPanel.setLayout(new BoxLayout(inputFieldsPanel, BoxLayout.Y_AXIS));
        inputFieldsPanel.setBorder(BorderFactory.createTitledBorder("Game Inputs"));

        pickedCardsPanel = new JPanel();
        pickedCardsPanel.setLayout(new BoxLayout(pickedCardsPanel, BoxLayout.Y_AXIS));
        pickedCardsPanel.setBorder(BorderFactory.createTitledBorder("Player Hands"));

        communityCardsDisplayPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        communityCardsDisplayPanel.setBorder(BorderFactory.createTitledBorder("Community Cards"));
        communityCardsDisplayPanel.setBackground(new Color(0, 100, 0));

        cardSelectionPanel = new JPanel(new GridLayout(4, 13, 3, 3));
        cardSelectionPanel.setBorder(BorderFactory.createTitledBorder("Select Cards"));

        JPanel resultsPanel = new JPanel(new BorderLayout());
        resultsPanel.setBorder(BorderFactory.createTitledBorder("Simulation Results"));

        // --- Create and Add Core Components ---
        Integer[] playerCounts = {2, 3, 4, 5, 6, 7, 8, 9, 10};
        playerCountSelector = new JComboBox<>(playerCounts);
        playerCountSelector.addActionListener(e -> generatePlayerInputFields((int) playerCountSelector.getSelectedItem()));

        flopField = new JTextField(20); // Give a default size
        turnField = new JTextField(20);
        simulationsField = new JTextField("10000", 10); // Give a default size

        resultArea = new JTextArea("Results will be displayed here.");
        resultArea.setEditable(false);
        resultArea.setFont(new Font("Monospaced", Font.PLAIN, 14));
        resultsPanel.add(new JScrollPane(resultArea), BorderLayout.CENTER);

        runButton = new JButton("Run Simulation");
        resetButton = new JButton("Reset");
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.CENTER));
        buttonPanel.add(runButton);
        buttonPanel.add(resetButton);
        resultsPanel.add(buttonPanel, BorderLayout.SOUTH);

        displayAvailableCards();

        // --- Layout Assembly ---
        mainContentPanel.add(new JScrollPane(inputFieldsPanel));
        mainContentPanel.add(new JScrollPane(pickedCardsPanel));

        topPanel.add(mainContentPanel, BorderLayout.CENTER);
        topPanel.add(communityCardsDisplayPanel, BorderLayout.SOUTH);

        bottomPanel.add(new JScrollPane(cardSelectionPanel), BorderLayout.CENTER);
        bottomPanel.add(resultsPanel, BorderLayout.EAST);

        add(topPanel, BorderLayout.CENTER);
        add(bottomPanel, BorderLayout.SOUTH);

        // --- Action Listeners ---
        runButton.addActionListener(e -> runSimulationAction());
        resetButton.addActionListener(e -> resetSelections());

        // --- Initial State ---
        generatePlayerInputFields(playerCounts[0]);
        pack();
        setLocationRelativeTo(null);
    }

    private void generatePlayerInputFields(int count) {
        playerCardFields.clear();
        playerDisplayPanels.clear();
        inputFieldsPanel.removeAll();
        pickedCardsPanel.removeAll();

        JPanel playerCountPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        playerCountPanel.add(new JLabel("Number of Players:"));
        playerCountPanel.add(playerCountSelector);
        inputFieldsPanel.add(playerCountPanel);

        for (int i = 0; i < count; i++) {
            JPanel playerInputRow = new JPanel(new FlowLayout(FlowLayout.LEFT));
            JLabel label = new JLabel("Player " + (i + 1) + " Cards:");
            JTextField field = new JTextField(20);
            playerInputRow.add(label);
            playerInputRow.add(field);
            inputFieldsPanel.add(playerInputRow);
            playerCardFields.add(field);

            JPanel displayPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
            displayPanel.setBorder(BorderFactory.createTitledBorder("Player " + (i + 1) + " Hand"));
            pickedCardsPanel.add(displayPanel);
            playerDisplayPanels.add(displayPanel);
        }

        JPanel flopPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        flopPanel.add(new JLabel("Flop Cards (Optional): "));
        flopPanel.add(flopField);
        inputFieldsPanel.add(flopPanel);

        JPanel turnPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        turnPanel.add(new JLabel("Turn Card (Optional):  "));
        turnPanel.add(turnField);
        inputFieldsPanel.add(turnPanel);

        JPanel simsPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        simsPanel.add(new JLabel("Number of Simulations:"));
        simsPanel.add(simulationsField);
        inputFieldsPanel.add(simsPanel);

        revalidate();
        repaint();
    }

    private void runSimulationAction() {
        runButton.setEnabled(false);
        resultArea.setText("Running simulation... Please wait.");

        final String flopInput = flopField.getText().trim();
        final String turnInput = turnField.getText().trim();
        final int simulations;
        try {
            simulations = Integer.parseInt(simulationsField.getText().trim());
        } catch (NumberFormatException ex) {
            resultArea.setText("❌ Error: Invalid number of simulations. Please enter a valid integer.");
            runButton.setEnabled(true);
            return;
        }

        final ArrayList<String> allPlayerCards = new ArrayList<>();
        for (JTextField field : playerCardFields) {
            allPlayerCards.add(field.getText().trim());
        }

        new Thread(() -> {
            final String resultText = PokerSimulation.runSimulations(allPlayerCards, flopInput, turnInput, simulations);
            SwingUtilities.invokeLater(() -> {
                resultArea.setText(resultText);
                runButton.setEnabled(true);
            });
        }).start();
    }

    private void resetSelections() {
        for (JTextField field : playerCardFields) {
            field.setText("");
        }
        for (JPanel panel : playerDisplayPanels) {
            panel.removeAll();
            panel.revalidate();
            panel.repaint();
        }

        communityCardsDisplayPanel.removeAll();
        communityCardsDisplayPanel.revalidate();
        communityCardsDisplayPanel.repaint();

        flopField.setText("");
        turnField.setText("");
        simulationsField.setText("10000");
        resultArea.setText("Inputs have been reset. Ready for new simulation.");

        for (JButton btn : cardButtons) {
            btn.setEnabled(true);
        }
        revalidate();
        repaint();
    }

    private void displayAvailableCards() {
        cardSelectionPanel.removeAll();
        TreeMap<String, ImageIcon> sortedCards = new TreeMap<>(cardImages);

        for (String cardName : sortedCards.keySet()) {
            JButton cardButton = new JButton(sortedCards.get(cardName));
            cardButton.setActionCommand(cardName);
            cardButton.setMargin(new Insets(2, 2, 2, 2));
            cardButton.addActionListener(new CardSelectionListener(cardButton, cardName));
            cardButtons.add(cardButton);
            cardSelectionPanel.add(cardButton);
        }
    }

    /**
     * ActionListener for each card button. Determines where to place the selected card.
     */
    private class CardSelectionListener implements ActionListener {
        private final JButton button;
        private final String cardName;

        public CardSelectionListener(JButton button, String cardName) {
            this.button = button;
            this.cardName = cardName;
        }

        @Override
        public void actionPerformed(ActionEvent e) {
            ImageIcon cardIcon = cardImages.get(cardName);

            // ✅ FIXED: Declare the lambda with its functional interface type.
            BiFunction<String, String, String> updateField =
                    (existingText, newCard) -> existingText.isEmpty() ? newCard : existingText + ", " + newCard;

            // --- 1. Try to fill a player's hand ---
            for (int i = 0; i < playerCardFields.size(); i++) {
                JTextField currentField = playerCardFields.get(i);
                String[] cardsInHand = currentField.getText().isEmpty() ? new String[0] : currentField.getText().split(", ");

                if (cardsInHand.length < 2) {
                    currentField.setText(updateField.apply(currentField.getText(), cardName));
                    playerDisplayPanels.get(i).add(new JLabel(cardIcon));
                    button.setEnabled(false);
                    revalidate();
                    repaint();
                    return;
                }
            }

            // --- 2. If hands are full, try to fill the flop ---
            String[] flopCards = flopField.getText().isEmpty() ? new String[0] : flopField.getText().split(", ");
            if (flopCards.length < 3) {
                flopField.setText(updateField.apply(flopField.getText(), cardName));
                communityCardsDisplayPanel.add(new JLabel(cardIcon));
                button.setEnabled(false);
                revalidate();
                repaint();
                return;
            }

            // --- 3. If flop is full, try to fill the turn ---
            if (turnField.getText().isEmpty()) { // ✅ This call is correct.
                turnField.setText(cardName);
                communityCardsDisplayPanel.add(new JLabel(cardIcon));
                button.setEnabled(false);
                revalidate();
                repaint();
            }
        }
    }

    // --- UTILITY METHODS ---
    private void loadCardImages() {

        //USE YOUR CARD LOCATION FOLDER HERE
        String basePath = "/Users/janekczajnik/Desktop/projects/solver/media/Playing Cards/PNG-cards-1.3/";
        String[] suits = {"clubs", "diamonds", "hearts", "spades"};
        String[] values = {"2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"};
        String[] valueNames = {"2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"};

        for (int i = 0; i < values.length; i++) {
            for (String suit : suits) {
                String cardName = valueNames[i] + " of " + suit;
                String imagePath = basePath + values[i] + "_of_" + suit + ".png";
                cardImages.put(cardName, loadImage(imagePath));
            }
        }
    }


    //For loading card
    private ImageIcon loadImage(String path) {
        try {
            ImageIcon icon = new ImageIcon(path);
            Image scaledImage = icon.getImage().getScaledInstance(60, 88, Image.SCALE_SMOOTH);
            return new ImageIcon(scaledImage);
        } catch (Exception e) {
            System.err.println("Error loading image: " + path);
            return new ImageIcon(new BufferedImage(60, 88, BufferedImage.TYPE_INT_RGB));
        }
    }
}