use pyo3::prelude::*;

/// Internal stone representation (0 = empty, 1 = black, -1 = white).
#[pyclass]
#[derive(Clone)]
pub struct Board {
    cells: [i8; 64],
    black_to_move: bool,
}

#[pymethods]
impl Board {
    /// Create the initial Othello position.
    #[new]
    pub fn new() -> Self {
        let mut cells = [0i8; 64];
        // central four stones
        cells[27] = -1;
        cells[28] = 1;
        cells[35] = 1;
        cells[36] = -1;
        Self {
            cells,
            black_to_move: true,
        }
    }

    /// Get the current player (true for black, false for white)
    pub fn get_black_to_move(&self) -> bool {
        self.black_to_move
    }

    /// Reset the board to the initial state.
    pub fn reset(&mut self) {
        *self = Self::new();
    }

    /// Return true if idx (0‑63) is a legal move for current side.
    pub fn is_legal(&self, idx: usize) -> bool {
        if self.cells[idx] != 0 {
            return false;
        }
        const DIRS: [i8; 8] = [-9, -8, -7, -1, 1, 7, 8, 9];
        let my = if self.black_to_move { 1 } else { -1 };
        let opp = -my;
        let _r = idx as i8 / 8;
        let c = idx as i8 % 8;
        for d in DIRS {
            // step in each direction
            let mut x = idx as i8 + d;
            let mut cnt = 0;
            while (0..64).contains(&x) {
                let _xr = x / 8;
                let xc = x % 8;
                // board wrap check
                if (d == -1 || d == 7 || d == -9) && xc > c {
                    break;
                }
                if (d == 1 || d == -7 || d == 9) && xc < c {
                    break;
                }
                let s = self.cells[x as usize];
                if s == opp {
                    cnt += 1;
                } else if s == my {
                    if cnt > 0 {
                        return true;
                    } else {
                        break;
                    }
                } else {
                    break;
                }
                x += d;
            }
        }
        false
    }

    /// Vector of all legal move indices for current side.
    pub fn legal_moves(&self) -> Vec<usize> {
        (0..64).filter(|&i| self.is_legal(i)).collect()
    }

    /// Play a move; returns number of stones flipped, or Err if illegal.
    pub fn play(&mut self, idx: usize) -> PyResult<usize> {
        if !self.is_legal(idx) {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Illegal move",
            ));
        }
        const DIRS: [i8; 8] = [-9, -8, -7, -1, 1, 7, 8, 9];
        let my = if self.black_to_move { 1 } else { -1 };
        let opp = -my;
        let _r = idx as i8 / 8;
        let c = idx as i8 % 8;
        let mut flipped = 0;
        self.cells[idx] = my;
        for d in DIRS {
            let mut buf: Vec<usize> = Vec::new();
            let mut x = idx as i8 + d;
            while (0..64).contains(&x) {
                let _xr = x / 8;
                let xc = x % 8;
                if (d == -1 || d == 7 || d == -9) && xc > c {
                    break;
                }
                if (d == 1 || d == -7 || d == 9) && xc < c {
                    break;
                }
                let s = self.cells[x as usize];
                if s == opp {
                    buf.push(x as usize);
                } else if s == my {
                    for i in &buf {
                        self.cells[*i] = my;
                    }
                    flipped += buf.len();
                    break;
                } else {
                    break;
                }
                x += d;
            }
        }
        self.black_to_move = !self.black_to_move;
        Ok(flipped as usize)
    }

    /// Return (black, white) counts.
    pub fn counts(&self) -> (u8, u8) {
        let mut b = 0u8;
        let mut w = 0u8;
        for &c in &self.cells {
            if c == 1 {
                b += 1;
            } else if c == -1 {
                w += 1;
            }
        }
        (b, w)
    }

    /// Python helper to get simple list for observation.
    pub fn as_list(&self) -> Vec<i8> {
        self.cells.to_vec()
    }
}

#[pymodule]
fn reversi_rl(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Board>()?;
    Ok(())
}

// -------- unit tests --------
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn initial_legal_moves() {
        let b = Board::new();
        let ls = b.legal_moves();
        assert_eq!(ls.len(), 4);
        for &mv in &[19usize, 26, 37, 44] {
            assert!(ls.contains(&mv));
        }
    }

    #[test]
    fn play_and_flip() {
        let mut b = Board::new();
        let flipped = b.play(19).unwrap();
        assert_eq!(flipped, 1);
        let (black, white) = b.counts();
        assert_eq!((black, white), (4, 1));
    }
}
