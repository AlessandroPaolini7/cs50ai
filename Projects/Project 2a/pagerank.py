import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Initializing a dictionary for storing probabilities and a list for storing pages with no outgoing links
    probabilities = {}
    links = corpus[page]
    available_links = []
    # If page has no outgoing links, return a probability distribution that chooses randomly among all pages with equal probability
    for i in corpus:
        if not corpus[i]:
            available_links.append(i)
            probabilities[i] = 0
    # Calculate probabilities for links with damping factor
    for link in links:
        probabilities[link] = damping_factor * (1 / len(links))
    
    # Calculate probabilities for pages with no outgoing links
    for link in available_links:
        probabilities[link] = (1 - damping_factor) / len(corpus)
    
    # Normalize probabilities so they sum to 1
    total_probability = sum(probabilities.values())
    for key in probabilities:
        probabilities[key] /= total_probability
    
    return probabilities


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initializing a list with the keys of the corpus dictionary, a dictorionary for storing created pages and a random page
    pages = list(corpus.keys())
    created_pages = {}
    page = random.choice(pages)
    # Assigning initial rank values to created pages
    for i in pages:
        created_pages[i] = 0
    created_pages[page] = 1 / n
    # Creating n-1 pages
    for i in range(n-1):
        new_page = transition_model(corpus, page, damping_factor)
        page = random.choices(list(new_page.keys()), weights=list(new_page.values()))[0]
        created_pages[page] += 1 / n
    return created_pages

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initializing pages number with the number of pages in the corpus, and two dictionaries for storing old and new rank values
    pages_number = len(corpus)
    old_dict = {}
    new_dict = {}
    # Iterating through all pages in the corpus and assigning them initial rank values
    for page in corpus:
        old_dict[page] = 1 / pages_number
    # Calculating new rank values until the difference between old and new values is less than 0.001
    while True:
        for page in corpus:
            temp = 0
            for linking_page in corpus:
                # Checking if page has links to other pages
                if page in corpus[linking_page]:
                    temp += (old_dict[linking_page] / len(corpus[linking_page]))
                # Checking if page has no links to other pages
                if len(corpus[linking_page]) == 0:
                    temp += (old_dict[linking_page]) / len(corpus)
            temp *= damping_factor
            temp += (1 - damping_factor) / pages_number
            new_dict[page] = temp
        difference = max([abs(new_dict[x] - old_dict[x]) for x in old_dict])
        # If the difference is less than 0.001, break the loop, this means that the rank values have converged
        if difference < 0.001:
            break
        else:
        # If the difference is more than 0.001, assign new rank values to old rank values and repeat the loop
            old_dict = new_dict.copy()

    return old_dict

if __name__ == "__main__":
    main()
